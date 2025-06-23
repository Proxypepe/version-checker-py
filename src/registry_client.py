import requests
from config import RegistryConfig, logger
from models.image import ImageReference 
from version import version_difference
from typing import Optional, Dict
from functools import lru_cache
import re


class VersionNormalizer:
    @staticmethod
    def normalize(version: str) -> tuple[str, str]:
        """
        Нормализует версию и возвращает (префикс, чистая версия)
        Примеры:
            "v1.2.3" -> ("v", "1.2.3")
            "2.5.0" -> ("", "2.5.0")
            "release-3.1" -> ("release-", "3.1")
        """
        match = re.match(r'^([^\d]*)([\d.]+.*)$', version)
        if match:
            return (match.group(1), match.group(2))
        return ("", version)

    @staticmethod
    def denormalize(prefix: str, version: str) -> str:
        return f"{prefix}{version}"


class RegistryClient:
    def __init__(self, registry_config: RegistryConfig, verify: bool = True):
        self.config = registry_config
        self.session = requests.Session()
        self.session.verify = verify
        
        if self.config.auth_type == "token":
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.token}"
            })
        elif self.config.auth_type == "basic":
            self.session.auth = (self.config.username, self.config.password)

    def check_version(self, image: ImageReference, desired_version: str) -> Dict:
        current_version = image.tag or self.get_tag_by_digest(image)
        diff_level, major_diff = version_difference(
            current_version,
            desired_version,
        )
        
        return {
            "current": current_version,
            "desired": desired_version,
            "status": diff_level,
            "major_diff": major_diff
        }

    @lru_cache(maxsize=100)
    def get_available_versions(self, image_name: str, registry: str, n: int = 500) -> list[str]:
        try:
            url = f'https://{registry}/v2/{image_name}/tags/list'
            r = self.session.get(url=url, params={'n': n})
            return r.json().get('tags', [])
        except Exception as e:
            logger.info(f"Failed to get versions for {image_name}: {str(e)}")
            return []


    def get_latest_version(self, image_name: str, registry: str, current_tag: str | None) -> str | None:
        if not current_tag:
            return None
        versions = self.get_available_versions(image_name, registry)
        prefix, _ = VersionNormalizer.normalize(current_tag)
        if not versions:
            return None

        matching_versions = []
        for v in versions:
            v_prefix, v_num = VersionNormalizer.normalize(v)
            if v_prefix == prefix:
                matching_versions.append((v_num, v))

        if not matching_versions:
            return None

        def version_key(v: str) -> tuple[int, ...]:
            try:
                return tuple(map(int, v.split('.')[:3]))
            except ValueError:
                return (0,)

        matching_versions.sort(reverse=True, key=lambda x: version_key(x[0]))
        return matching_versions[0][1]

    def get_tag_by_digest(self, image: ImageReference) -> Optional[str]:
        pass
    
    
    def update_config(self, new_config: RegistryConfig):
        self.config = new_config
        if self.config.auth_type == "token":
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.token}"
            })
        elif self.config.auth_type == "basic":
            self.session.auth = (self.config.username, self.config.password)
