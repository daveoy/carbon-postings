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
    k8s = Kubernetes()
    job_container = k8s.create_container(
        image="registry.carbonvfx.com/engineering/postings:transcode-latest",
        name="transcode",
        pull_policy="Always",
        args=src
    )
    job_pod_spec = k8s.create_pod_template(
        pod_name=f"{src.filename.split('.')[0]}-{src.date}-{src.time}",
        container=job_container
    )
    job_spec = k8s.create_job(
        job_name=f"{src.filename.split('.')[0]}-{src.date}-{src.time}",
        pod_template=job_pod_spec
    )
    logging.info(f"creating job: {src.filename.split('.')[0]}-{src.date}-{src.time}")
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job("postings", job_spec)
    return

class Kubernetes:
    def __init__(self):
        # Init Kubernetes
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    @staticmethod
    def create_container(image, name, pull_policy, args):
        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            args=[args]
        )
        return container

    @staticmethod
    def create_pod_template(pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )
        return pod_template

    @staticmethod
    def create_job(job_name, pod_template):
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )
        return job


if __name__ == "__main__":
    while True:
        for job in os.listdir(JOBS_ROOT):
            [start_transcode(x) for x in get_sources(job) if x.output.transcoded == False]