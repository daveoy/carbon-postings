import os
import glob
import logging
from postings import Source
from kubernetes import client
from kubernetes import config

config.load_incluster_config()
logging.basicConfig(level=logging.INFO)

JOBS_ROOT = '/mnt/jobs'
def get_sources(d: str):
    return [Source(x) for x in glob.glob(f"{os.path.join(JOBS_ROOT,d,'library/postings/source')}/**/*.mov",recursive=True)]

def start_transcode(src: Source):
    logging.info(f"creating job: {src.filename.split('.')[0]}-{src.date}-{src.time}")
    job_spec = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata":{
            "name": f"{src.filename.split('.')[0]}-{src.date}-{src.time}".replace('_','-').lower(),
            "namespace": "postings"
        },
        "spec":{
            "template":{
                "spec":{
                    "restartPolicy": "Never",
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
                                "path": "/vfx/vfx/Jobs/tmobile_metro_235890",
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
                            "name": f"{src.filename.split('.')[0]}-{src.date}-{src.time}".replace('_','-').lower(),
                            "image": "registry.carbonvfx.com/engineering/postings:transcode-latest",
                            "args":[
                                src.path
                            ],
                            "volumeMounts":[
                                {   
                                    "name": "secrets-store-inline",
                                    "mountPath": "/secrets-store",
                                    "readOnly": True
                                },
                                {   
                                    "name": "weka-jobs",
                                    "mountPath": "/mnt/jobs/tmobile_metro_235890",
                                    "readOnly": False
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job("postings", job_spec)
    return

if __name__ == "__main__":
    while True:
        for job in os.listdir(JOBS_ROOT):
            [start_transcode(x) for x in get_sources(job) if x.output.transcoded == False]