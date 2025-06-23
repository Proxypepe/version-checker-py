import yaml
import os
from typing import Optional
from dataclasses import dataclass
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('version-checker')

@dataclass
class SHA256Resolution:
    tag: str
    hash: str

@dataclass
class ImageConfig:
    name: str
    desired_tag: str
    pined_major: Optional[int] = None
    resolve_sha256: Optional[list[SHA256Resolution]] = None

@dataclass
class RegistryConfig:
    url: str
    auth_type: str
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

@dataclass
class AppConfig:
    namespace_list: list[str]
    images: list[ImageConfig]
    registry: RegistryConfig
    shedule: str

def load_config(config_path: str = "config.yaml") -> AppConfig:
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f) or {}    
    registry_config = config_data.get('registry', {})
    
    if registry_config.get('auth_type') == 'token':
        token = os.getenv('REGISTRY_TOKEN')
        if not token:
            raise ValueError("REGISTRY_TOKEN environment variable is required for token auth")
        registry_config['token'] = token
    else:
        username = os.getenv('REGISTRY_USERNAME')
        password = os.getenv('REGISTRY_PASSWORD')
        if username and password:
            registry_config.update({
                'username': username,
                'password': password
            })
    
    images_config = []
    for img in config_data.get('images', []):
        sha256_resolutions = None
        if 'resolve_sha256' in img:
            sha256_resolutions = [
                SHA256Resolution(tag=r['tag'], hash=r['hash'])
                for r in img['resolve_sha256']
            ]
        
        images_config.append(
            ImageConfig(
                name=img['name'],
                desired_tag=img['desired_tag'],
                pined_major=img.get('pined_major'),
                resolve_sha256=sha256_resolutions
            )
        )
    
    return AppConfig(
        namespace_list=config_data.get('namespace_list', []),
        images=images_config,
        registry=RegistryConfig(**registry_config),
        shedule=config_data.get('shedule', '')
    )