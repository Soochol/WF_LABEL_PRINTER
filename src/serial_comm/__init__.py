"""시리얼 통신 모듈"""

# MCUMonitor는 PyQt6 의존성이 있어 GUI에서만 import
from .mac_parser import MACParser

__all__ = ["MACParser"]
