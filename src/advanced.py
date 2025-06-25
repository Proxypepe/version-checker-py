import re
from functools import total_ordering
from typing import List, Optional, Tuple

@total_ordering
class AdvancedVersion:
    def __init__(self, version_str: str):
        self.original = version_str
        self.prefix, self.numbers, self.suffix = self._parse_version(version_str)
    
    def _parse_version(self, version_str: str) -> Tuple[str, List[int], str]:
        # Разбираем версию на компоненты
        match = re.match(r'^([^\d]*)([\d.]+)([^\d]*.*)$', version_str)
        if not match:
            return ("", [0], "")
        
        prefix = match.group(1)
        num_part = match.group(2)
        suffix = match.group(3)
        
        # Извлекаем числовые компоненты
        numbers = []
        for n in num_part.split('.'):
            if n.isdigit():
                numbers.append(int(n))
            elif numbers:  # Для случаев типа "1.2.3-beta.4"
                break
        
        return (prefix, numbers, suffix)
    
    def __eq__(self, other):
        if not isinstance(other, AdvancedVersion):
            return False
        return self.numbers == other.numbers
    
    def __lt__(self, other):
        if not isinstance(other, AdvancedVersion):
            return NotImplemented
        return self.numbers < other.numbers
    
    def __str__(self):
        return self.original
    
    def to_matching_format(self, numbers: List[int]) -> str:
        """Форматирует числовые компоненты в стиле оригинальной версии"""
        num_str = ".".join(map(str, numbers))
        return f"{self.prefix}{num_str}{self.suffix}"

class VersionComparator:
    VERSION_PATTERNS = [
        r'^v?\d+\.\d+\.\d+',       # v1.2.3 или 1.2.3
        r'^release-\d+\.\d+\.\d+', # release-1.2.3
        r'^\d+\.\d+\.\d+-[a-z]+',  # 1.2.3-alpha
        r'^\d+\.\d+\.\d+_\d+',     # 1.2.3_4
    ]
    
    @classmethod
    def is_version_valid(cls, version_str: str) -> bool:
        """Проверяет, соответствует ли строка одному из известных форматов"""
        return any(re.match(pattern, version_str) for pattern in cls.VERSION_PATTERNS)
    
    @classmethod
    def get_latest_matching_version(cls, current_version: str, available_versions: List[str]) -> Optional[str]:
        """
        Находит последнюю версию, соответствующую формату current_version
        
        Примеры:
          current: v1.2.3 → ищет vX.Y.Z
          current: release-1.2.3 → ищет release-X.Y.Z
        """
        if not available_versions:
            return None
        
        current = AdvancedVersion(current_version)
        matching_versions = []
        
        for v in available_versions:
            if not cls.is_version_valid(v):
                continue
            
            version = AdvancedVersion(v)
            # Совпадение префикса и суффикса
            if version.prefix == current.prefix and version.suffix == current.suffix:
                matching_versions.append(version)
        
        if not matching_versions:
            return None
        
        latest = max(matching_versions)
        return str(latest)
    
    @classmethod
    def compare_versions(cls, current: str, desired: str) -> dict:
        """
        Сравнивает версии с учетом их формата
        Возвращает:
        {
            "current": "v1.2.3",
            "desired": "v1.3.0",
            "latest": "v1.4.2",
            "status": "outdated|match|error",
            "is_up_to_date": bool
        }
        """
        current_ver = AdvancedVersion(current)
        desired_ver = current_ver.to_matching_format(
            AdvancedVersion(desired).numbers
        ) if desired else None
        
        return {
            "current": current,
            "desired": desired_ver,
            "status": cls._get_status(current_ver, desired_ver),
            "is_up_to_date": desired_ver and current_ver >= AdvancedVersion(desired_ver)
        }
    
    @classmethod
    def _get_status(cls, current: AdvancedVersion, desired: Optional[str]) -> str:
        if not desired:
            return "unknown"
        if current == AdvancedVersion(desired):
            return "match"
        if current < AdvancedVersion(desired):
            return "outdated"
        return "newer"

# Пример использования
if __name__ == "__main__":
    test_cases = [
        ("v1.20.1", "v1.22.0", ["v1.22.0", "v1.21.5", "v1.20.2"]),
        ("release-1.13.3", "release-1.15.0", ["release-1.15.0", "release-1.14.2"]),
        ("2.3.4-lts", "2.4.0", ["2.4.0-lts", "2.3.5-lts"]),
        ("1.2.3_4", "1.2.4", ["1.2.4_4", "1.2.3_5"]),
    ]
    
    for current, desired, available in test_cases:
        print(f"\nCurrent: {current}, Desired: {desired}")
        latest = VersionComparator.get_latest_matching_version(current, available)
        result = VersionComparator.compare_versions(current, desired)
        result["latest"] = latest
        print(f"Latest matching: {latest}")
        print(f"Comparison result: {result}")
