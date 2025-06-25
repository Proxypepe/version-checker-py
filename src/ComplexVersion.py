import re
from typing import Optional, Tuple, List
from functools import total_ordering

@total_ordering
class ComplexVersion:
    def __init__(self, version_str: str):
        self.original = version_str
        self.prefix = ""
        self.numbers = []
        self.suffix = ""
        self._parse_version(version_str)
    
    def _parse_version(self, version_str: str):
        # Разделяем префикс, числовую часть и суффикс
        match = re.match(r'^([^\d]*)([\d.]+)(.*)$', version_str)
        if not match:
            self.numbers = [0]
            return
        
        self.prefix = match.group(1)
        num_part = match.group(2)
        self.suffix = match.group(3)
        
        # Парсим числовую часть
        self.numbers = [int(n) for n in num_part.split('.') if n.isdigit()]
        if not self.numbers:
            self.numbers = [0]
    
    def __eq__(self, other):
        if not isinstance(other, ComplexVersion):
            return False
        return self.numbers == other.numbers
    
    def __lt__(self, other):
        if not isinstance(other, ComplexVersion):
            return NotImplemented
        return self.numbers < other.numbers
    
    def __str__(self):
        return self.original
    
    def to_comparable(self, other_version: str) -> 'ComplexVersion':
        """Создает версию для сравнения с тем же суффиксом"""
        other = ComplexVersion(other_version)
        return ComplexVersion(f"{self.prefix}{'.'.join(map(str, other.numbers))}{self.suffix}")

class VersionChecker:
    def __init__(self, registry_client):
        self.registry = registry_client
    
    def get_latest_matching_version(self, current_version: str, image_name: str) -> Optional[str]:
        """
        Получает последнюю версию, сохраняя структуру current_version
        Пример:
          current: 2.399.1-lts-rhel-jdk
          available: [2.444.1-lts-rhel-jdk, 2.400.0-lts-rhel-jdk]
          возвращает: 2.444.1-lts-rhel-jdk
        """
        current = ComplexVersion(current_version)
        all_versions = self.registry.get_all_versions(image_name)
        
        if not all_versions:
            return None

        # Фильтруем версии с таким же суффиксом
        matching_versions = []
        for v in all_versions:
            version = ComplexVersion(v)
            if version.suffix == current.suffix:
                matching_versions.append(version)
        
        if not matching_versions:
            return None
        
        # Находим максимальную версию
        latest = max(matching_versions)
        return str(latest)
    
    def check_version(self, current_version: str, desired_version: str, image_name: str) -> dict:
        """
        Сравнивает версии с учетом сложных форматов
        """
        current = ComplexVersion(current_version)
        desired = current.to_comparable(desired_version) if desired_version else None
        
        latest = self.get_latest_matching_version(current_version, image_name)
        latest_comparable = current.to_comparable(latest) if latest else None
        
        return {
            "current": str(current),
            "desired": str(desired) if desired else None,
            "latest": latest,
            "is_up_to_date": (
                latest_comparable >= desired if desired and latest_comparable 
                else False
            ),
            "status": self._get_status(current, desired, latest_comparable)
        }
    
    def _get_status(self, current, desired, latest):
        if not latest:
            return "unknown"
        if not desired:
            return "latest" if current >= latest else "outdated"
        return "match" if current >= desired else "mismatch"

# Пример использования
if __name__ == "__main__":
    class MockRegistry:
        def get_all_versions(self, image):
            return [
                "2.444.1-lts-rhel-jdk",
                "2.400.0-lts-rhel-jdk",
                "2.399.2-lts-rhel-jdk",
                "3.0.0-beta",
                "2.500.0-other-suffix"
            ]
    
    checker = VersionChecker(MockRegistry())
    
    # Пример с complex версией
    current = "2.399.1-lts-rhel-jdk"
    desired = "2.444.1"
    result = checker.check_version(current, desired, "test/image")
    
    print(f"Current: {result['current']}")
    print(f"Desired: {result['desired']}")  # 2.444.1-lts-rhel-jdk
    print(f"Latest: {result['latest']}")    # 2.444.1-lts-rhel-jdk
    print(f"Status: {result['status']}")    # mismatch или match
    print(f"Is up-to-date: {result['is_up_to_date']}")
