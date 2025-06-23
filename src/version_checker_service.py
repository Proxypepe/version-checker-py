import time

from config import load_config
from kubernetes_client import KubernetesClient
from metrics import MetricsCollector
from registry_client import RegistryClient
from typing import Optional 
from functools import lru_cache
from config import logger


class VersionCheckerService:
    def __init__(self):
        self.config = load_config()
        self.k8s_client = KubernetesClient()
        self.registry_client = RegistryClient(self.config.registry)
        self.metrics = MetricsCollector()

    def check_versions(self):
        logger.info("Starting version check...")
        images = self.k8s_client.get_pod_images(self.config.namespace_list)
        for image in images:
            logger.info(f'Working with {image.name} pod: {image.pod_name} in namespace: {image.namespace}')
            if not image.tag and image.digest:
                image.tag = self.resolve_sha_by_config(image.full_name, image.digest)
            desired_version = self.get_desired_version(image.full_name)
            if not desired_version:
                continue
            status = self.registry_client.check_version(
                image,
                desired_version
            )
            latest_version = self.registry_client.get_latest_version(image.name, image.registry, image.tag)
            self.metrics.update(image, desired_version, latest_version, status)
        
        logger.info("Version check completed")


    @lru_cache(maxsize=100)
    def get_desired_version(self, image_name: str) -> Optional[str]:
        for img in self.config.images:
            if img.name == image_name:
                return img.desired_tag
        return None


    @lru_cache(maxsize=100)
    def resolve_sha_by_config(self, image_name: str, sha256: str) -> Optional[str]:
        for img in self.config.images:
            if img.name == image_name:
                for sha256_catalog in img.resolve_sha256:
                    if sha256_catalog.hash == sha256:
                        return sha256_catalog.tag
        return None


    def reload_config(self):
        try:
            self.config = load_config()
            self.registry_client.update_config(self.config.registry)
            return True
        except Exception as e:
            logger.info(f"Config reload failed: {e}")
            return False
