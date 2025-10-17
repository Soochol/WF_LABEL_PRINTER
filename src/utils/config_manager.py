"""
YAML 설정 파일 관리자
"""

import yaml
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """YAML 설정 파일 관리자"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config_path = config_path
        self._config: Optional[dict] = None
        self.load()

    def load(self) -> dict:
        """설정 로드"""
        path = Path(self.config_path)

        if not path.exists():
            self._config = {}
            return self._config

        with open(path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        return self._config

    def save(self, config: Optional[dict] = None) -> None:
        """
        설정 저장

        Args:
            config: 저장할 설정 dict (None이면 현재 설정 저장)
        """
        if config is not None:
            self._config = config

        path = Path(self.config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self._config, f, allow_unicode=True, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정 값 조회 (점 표기법 지원)

        Args:
            key: 키 (점 표기법 지원: "printer.vendor_id")
            default: 기본값

        Returns:
            설정 값

        Example:
            >>> config.get("printer.vendor_id")
            0x0A5F
            >>> config.get("serial.port", "COM3")
            'COM3'
        """
        if self._config is None:
            return default

        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        설정 값 저장 (점 표기법 지원)

        Args:
            key: 키 (점 표기법 지원)
            value: 값

        Example:
            >>> config.set("printer.vendor_id", 0x0A5F)
            >>> config.set("serial.port", "COM5")
        """
        if self._config is None:
            self._config = {}

        keys = key.split('.')
        current = self._config

        # 중첩 dict 생성
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        # 마지막 키에 값 설정
        current[keys[-1]] = value

    def reload(self) -> dict:
        """설정 파일 다시 로드"""
        return self.load()

    @property
    def config(self) -> dict:
        """전체 설정 dict"""
        return self._config or {}
