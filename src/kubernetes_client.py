from kubernetes import client, config
from models.image import ImageReference
from typing import List
from urllib.parse import urlparse
from config import logger

class KubernetesClient:
    def __init__(self):
        try:
            config.load_kube_config()
        except:
            config.load_incluster_config()
        self.v1 = client.CoreV1Api()


    def get_pod_images(self, namespace_list: List[str] = None) -> List[ImageReference]:
        images = []
        namespaces = namespace_list if namespace_list else [None]
        
        for ns in namespaces:
            pods = self.v1.list_namespaced_pod(ns).items if ns else self.v1.list_pod_for_all_namespaces().items
            
            for pod in pods:
                for container in pod.spec.containers:
                    try:
                        images.append(self.parse_image(
                            container.image,
                            container.name,
                            pod.metadata.namespace
                        ))
                    except Exception as e:
                        logger.info(f'Image: {container.image} with name: {container.name} - {e}')
        return images


    def parse_image(self, image: str, pod_name: str, namespace: str) -> ImageReference:
        parsed = urlparse(f"docker://{image}")
        image_path = parsed.path.lstrip('/')
        registry = parsed.netloc
        if '/' not in image_path:
            image_path = f"{parsed.netloc}/{image_path}"
            registry = 'registry-1.io'
        tag = None
        digest = None
        if '@' in image_path:
            splited = image_path.split('@')
            if ':' in splited[0]:
                tag = splited[0].split(':')[1]
                image_path = splited[0].split(':')[0]
                if 'sha256:' in splited[1]:
                    digest = splited[1]
            elif ':' not in splited[0]:
                digest = splited[1]
                image_path = splited[0]
            else:
                raise ValueError(image_path)
        elif ':' in image_path:
            splited = image_path.split(':')
            tag = splited[1]
            image_path = splited[0]
        else:
            return ImageReference(
                name=image_path,
                pod_name=pod_name,
                namespace=namespace,
                registry=registry,
                tag=tag,
                digest=digest
            )
        return ImageReference(
            name=image_path,
            pod_name=pod_name,
            namespace=namespace,
            registry=registry,
            tag=tag,
            digest=digest
        )
