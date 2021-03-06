import kubernetes as kube

client = kube.client


def create_job(app_id, cmd, img):

    kube.config.load_kube_config('/home/pickle/.kube/config')

    obj_meta = kube.client.V1ObjectMeta(
        name=app_id)

    isgx = kube.client.V1VolumeMount(
        mount_path="/dev/isgx",
        name="dev-isgx"
    )

    devisgx = kube.client.V1Volume(
        name="dev-isgx",
        host_path=kube.client.V1HostPathVolumeSource(
            path="/dev/isgx"
        )
    )

    container_spec = kube.client.V1Container(
        command=cmd,
        image=img,
        image_pull_policy="Always",
        name=app_id,
        tty=True,
        volume_mounts=[isgx],
        security_context=kube.client.V1SecurityContext(
            privileged=True
        ))

    pod_spec = kube.client.V1PodSpec(
        containers=[container_spec],
        restart_policy="OnFailure",
        volumes=[devisgx])

    pod = kube.client.V1PodTemplateSpec(
        metadata=obj_meta,
        spec=pod_spec)

    job_spec = kube.client.V1JobSpec(
        parallelism=1,
        template=pod)

    job = kube.client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=obj_meta,
        spec=job_spec)

    batch_v1 = kube.client.BatchV1Api()
    batch_v1.create_namespaced_job("default", job)

    return job


def create_service(app_id):
    api = kube.client.CoreV1Api()

    svc_meta = {
        "name": 'service-' + app_id,
        "labels": {
            "app": 'service-' + app_id
        }
    }

    svc_spec = {
        "ports": [{
            "protocol": "TCP",
            "port": 5000,
            "targetPort": 5000
        }],
        "selector": {
            "app": 'service-' + app_id
        },
        "type": "NodePort"
    }
    svc = kube.client.V1Service(
        spec=svc_spec, api_version="v1", kind="Service", metadata=svc_meta)

    print('Creating service...')

    api.create_namespaced_service(namespace='default', body=svc)


app_id = 'sconericles'
create_job(app_id, ['/bin/bash'], '10.11.5.6:5000/sconericles:cast')

#create_service(app_id)
