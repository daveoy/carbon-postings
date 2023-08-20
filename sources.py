import os
import glob
import json
import uuid
import time
import sys

from postings import Source
from kubernetes import client
from kubernetes import config

config.load_incluster_config()

JOBS_ROOT = '/mnt/jobs'
def get_sources(d: str):
    return [Source(x) for x in glob.glob(f"{os.path.join(JOBS_ROOT,d,'library/postings/source')}/*/*/*.mov",recursive=True)]

def check_job_running(path):
    batch_api = client.BatchV1Api()
    jobs = batch_api.list_namespaced_job(namespace='postings')
    for job in jobs.items:
        if job.metadata.annotations['source/path'] == path:
            return True
    return False

def start_transcode(src: Source):
    job_id = str(uuid.uuid4())
    print(
        json.dumps({
            "job":job_id,
            "project": src.project,
            "date": src.date,
            "time": src.time,
            "filename": src.filename
        })
    )
    job_spec = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata":{
            "name": job_id,
            "namespace": "postings",
            "annotations": {
                "source/path": src.path,
                "source/project": src.project,
                "source/date": src.date,
                "source/time": src.time,
                "source/filename": src.filename,
                "transcode/path": src.output.path,
                "transcode/filename": src.output.filename,
                "transcode/date": src.output.date
            }
        },
        "spec":{
            "ttlSecondsAfterFinished":10,
            "template":{
                "spec":{
                    "restartPolicy":"OnFailure",
                    "volumes":[
                        {
                            "name": "secrets-store-inline",
                            "csi":{
                                "driver": "secrets-store.csi.k8s.io",
                                "readOnly": True,
                                "volumeAttributes":{
                                    "secretProviderClass": "regcred",
                                },
                            }
                        },
                        {
                            "name": "weka-jobs",
                            "nfs":{
                                "server": "10.70.50.117",
                                "path": "/vfx/vfx/Jobs/",
                                "readOnly": False,
                            }
                        }
                    ],
                    "imagePullSecrets":[
                        {
                            "name": "regcred"
                        },
                    ],
                    "serviceAccountName": "image-puller",
                    "containers":[
                        {
                            "name": job_id,
                            "image": "registry.carbonvfx.com/engineering/postings:transcode-1692448115",
                            "imagePullPolicy":"Always",
                            "args":[
                                src.path
                            ],
                            "resources":{
                                "limits":{
                                    "cpu":"2",
                                    "memory":"2G"
                                },
                                "requests":{
                                    "cpu":"1",
                                    "memory":"1G"
                                }
                            },
                            "volumeMounts":[
                                {   
                                    "name": "secrets-store-inline",
                                    "mountPath": "/secrets-store",
                                    "readOnly": True
                                },
                                {   
                                    "name": "weka-jobs",
                                    "mountPath": "/mnt/jobs/",
                                    "readOnly": False
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    try:
        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job("postings", job_spec)
    except client.exceptions.ApiException as e:
        if e.status == 409:
            print(f"job already exists")
            print(e)
        else:
            raise e
    return

if __name__ == "__main__":
    while True:
        start_time = time.time()
        print(
            json.dumps({
                "msg": f"starting scan loop {start_time}"
            })
        )
        sys.stdout.flush()
        for job in os.listdir(JOBS_ROOT):
            [start_transcode(x) for x in get_sources(job) if x.output.transcoded == False and check_job_running(x.path) == False]
        time.sleep(60)
        loop_time = time.time() - start_time
        print(
            json.dumps({
                "msg": f"finished scan loop in {loop_time} seconds"
            })
        )
        sys.stdout.flush()