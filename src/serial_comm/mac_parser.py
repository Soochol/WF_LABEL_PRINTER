"""
MAC 주소 파서
"""

import re
from typing import Optional


class MACParser:
    """MAC 주소 파서 (device id 추출)"""

    # 정규식 패턴: "device id: PSAD0CF1327829495"
    PATTERN = re.compile(r'device id:\s*([A-Z0-9]+)', re.IGNORECASE)

    # MAC 주소 검증 패턴 (영문 대문자 + 숫자)
    MAC_VALIDATION_PATTERN = re.compile(r'^[A-Z0-9]+$')

    @staticmethod
    def parse(log_line: str) -> Optional[str]:
        """
        로그 라인에서 MAC 주소 추출

        Args:
            log_line: 로그 라인 문자열

        Returns:
            MAC 주소 또는 None

        Example:
            >>> MACParser.parse("device id: PSAD0CF1327829495")
            'PSAD0CF1327829495'
            >>> MACParser.parse("other log message")
            None
        """
        match = MACParser.PATTERN.search(log_line)
        if match:
            mac = match.group(1).upper()  # 대문자로 변환
            return mac
        return None

    @staticmethod
    def validate(mac_address: str) -> bool:
        """
        MAC 주소 형식 검증

        Args:
            mac_address: MAC 주소 문자열

        Returns:
            유효 여부

        Example:
            >>> MACParser.validate("PSAD0CF1327829495")
            True
            >>> MACParser.validate("invalid-mac")
            False
        """
        if not mac_address:
            return False

        return MACParser.MAC_VALIDATION_PATTERN.match(mac_address) is not None

    @staticmethod
    def extract_from_logs(logs: list) -> Optional[str]:
        """
        여러 로그 라인에서 MAC 주소 추출 (첫 번째 매칭만 반환)

        Args:
            logs: 로그 라인 리스트

        Returns:
            MAC 주소 또는 None

        Example:
            >>> logs = [
                "Starting system...",
                "device id: PSAD0CF1327829495",
                "System ready"
            ]
            >>> MACParser.extract_from_logs(logs)
            'PSAD0CF1327829495'
        """
        for line in logs:
            mac = MACParser.parse(line)
            if mac:
                return mac
        return None
