from pydantic import BaseModel
from typing import Optional


class ImageReference(BaseModel):
    name: str
    registry: str
    pod_name: str
    namespace: str
    tag: Optional[str] = None
    digest: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.registry}/{self.name}" 
