from dataclasses import dataclass
import re

@dataclass
class Version:
    """Класс для хранения и сравнения версий"""
    original: str
    major: int = 0
    minor: int = 0
    patch: int = 0
    prefix: str = ""
    suffix: str = ""
    
    def __init__(self, version_str: str):
        self.original = version_str
        self._parse_version(version_str)
    
    def _parse_version(self, version_str: str):
        # Удаляем ведущие/конечные пробелы и "v" в начале
        clean_str = version_str.strip().lstrip('vV')
        self.prefix = "v" if version_str.lower().startswith('v') else ""
        
        # Разбиваем на числовые части и суффикс
        parts = re.split(r'[.-]', clean_str, maxsplit=3)
        num_parts = []
        suffix_parts = []
        
        for part in parts:
            if part.isdigit():
                num_parts.append(int(part))
            else:
                # Пытаемся разделить цифры и буквы (например, "1beta" -> 1, "beta")
                digit_part = re.match(r'^\d+', part)
                if digit_part:
                    num_parts.append(int(digit_part.group()))
                    suffix_parts.append(part[digit_part.end():])
                else:
                    suffix_parts.append(part)
                break  # Прерываем после первого нечислового компонента
        
        # Заполняем основные компоненты версии
        self.major = num_parts[0] if len(num_parts) > 0 else 0
        self.minor = num_parts[1] if len(num_parts) > 1 else 0
        self.patch = num_parts[2] if len(num_parts) > 2 else 0
        self.suffix = "".join(suffix_parts) if suffix_parts else ""
    
    def __str__(self):
        return self.original
    
    def is_valid(self) -> bool:
        """Проверяет, является ли версия валидной"""
        return self.major != 0 or self.minor != 0 or self.patch != 0
    
    def compare(self, other: 'Version') -> int:
        """Сравнивает версии: возвращает -1 если self < other, 0 если ==, 1 если >"""
        if not self.is_valid() or not other.is_valid():
            return 0
        
        if self.major != other.major:
            return -1 if self.major < other.major else 1
        if self.minor != other.minor:
            return -1 if self.minor < other.minor else 1
        if self.patch != other.patch:
            return -1 if self.patch < other.patch else 1
        return 0

def version_difference(
    current_version: str,
    desired_version: str,
) -> tuple[str, int]:
    """
    Анализирует разницу между версиями.
    
    Args:
        current_version: текущая версия (например, "v1.2.3")
        desired_version: желаемая версия (например, "2.0.0-beta")
        available_versions: список доступных версий
    
    Returns:
        tuple: (difference_level, nearest_version, is_dangerous, major_diff)
        - difference_level: "major", "minor", "patch", "same", "invalid"
        - major_diff: разница в major версиях (current - desired)
    """
    current = Version(current_version)
    desired = Version(desired_version)
    
    # Проверка валидности версий
    if not current.is_valid() or not desired.is_valid():
        return ("invalid", 0)
    
    # Если версии одинаковые
    if current.original == desired.original:
        return ("same", 0)
    # Разница в major версиях
    major_diff = current.major - desired.major
    
    # Определяем уровень изменений
    if current.major != desired.major:
        # Проверяем, есть ли в available версии с тем же major
        return (
            "major",
            major_diff
        )
    elif current.minor != desired.minor:
        return ("minor", major_diff)
    else:
        return ("patch", major_diff)
