"""
MAC 파서 테스트
"""

import pytest
from src.serial_comm.mac_parser import MACParser


def test_parse_valid_mac():
    """유효한 MAC 주소 파싱 테스트"""
    line = "device id: PSAD0CF1327829495"
    mac = MACParser.parse(line)

    assert mac == "PSAD0CF1327829495"


def test_parse_with_extra_text():
    """추가 텍스트가 있는 로그 파싱 테스트"""
    line = "[12:34:56] device id: PSAD0CF1327829495 - OK"
    mac = MACParser.parse(line)

    assert mac == "PSAD0CF1327829495"


def test_parse_case_insensitive():
    """대소문자 무관 파싱 테스트"""
    line = "Device ID: psad0cf1327829495"
    mac = MACParser.parse(line)

    assert mac == "PSAD0CF1327829495"  # 대문자로 변환


def test_parse_no_match():
    """매칭되지 않는 로그 파싱 테스트"""
    line = "This is a normal log message"
    mac = MACParser.parse(line)

    assert mac is None


def test_parse_empty_string():
    """빈 문자열 파싱 테스트"""
    mac = MACParser.parse("")
    assert mac is None


def test_validate_valid_mac():
    """유효한 MAC 주소 검증 테스트"""
    assert MACParser.validate("PSAD0CF1327829495") == True
    assert MACParser.validate("1234567890ABCDEF") == True


def test_validate_invalid_mac():
    """유효하지 않은 MAC 주소 검증 테스트"""
    assert MACParser.validate("") == False
    assert MACParser.validate("psad0cf1327829495") == False  # 소문자
    assert MACParser.validate("PSAD-0CF-132") == False  # 특수문자
    assert MACParser.validate("PSAD 0CF 132") == False  # 공백


def test_extract_from_logs():
    """여러 로그에서 MAC 추출 테스트"""
    logs = [
        "Starting system...",
        "Initializing hardware...",
        "device id: PSAD0CF1327829495",
        "System ready",
    ]

    mac = MACParser.extract_from_logs(logs)
    assert mac == "PSAD0CF1327829495"


def test_extract_from_logs_multiple_matches():
    """여러 MAC이 있을 때 첫 번째만 반환 테스트"""
    logs = [
        "device id: PSAD0CF1327829495",
        "device id: TEST1234567890ABC",
    ]

    mac = MACParser.extract_from_logs(logs)
    assert mac == "PSAD0CF1327829495"  # 첫 번째만


def test_extract_from_logs_no_match():
    """MAC이 없는 로그에서 추출 테스트"""
    logs = [
        "Starting system...",
        "System ready",
    ]

    mac = MACParser.extract_from_logs(logs)
    assert mac is None


def test_extract_from_empty_logs():
    """빈 로그 리스트에서 추출 테스트"""
    mac = MACParser.extract_from_logs([])
    assert mac is None


def test_parse_various_formats():
    """다양한 형식 파싱 테스트"""
    test_cases = [
        ("device id: ABC123", "ABC123"),
        ("device id:ABC123", "ABC123"),  # 공백 없음
        ("device id:  ABC123", "ABC123"),  # 공백 여러개
        ("Device Id: abc123", "ABC123"),  # 대소문자 혼합
    ]

    for line, expected in test_cases:
        mac = MACParser.parse(line)
        assert mac == expected, f"Failed for: {line}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
