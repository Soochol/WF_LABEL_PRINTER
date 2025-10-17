"""
PRN 파서 테스트
"""

import pytest
from pathlib import Path
from src.printer.prn_parser import PRNParser
from src.printer.exceptions import TemplateNotFoundError, InvalidVariableError


@pytest.fixture
def template_path():
    """실제 PRN 템플릿 파일 경로"""
    return "templates/PSA_LABEL_ZPL_with_mac_address.prn"


@pytest.fixture
def parser(template_path):
    """PRN 파서 인스턴스"""
    return PRNParser(template_path)


def test_load_template(template_path):
    """템플릿 로드 테스트"""
    parser = PRNParser(template_path)

    assert parser.template is not None
    assert len(parser.template) > 0
    assert "^XA" in parser.template  # ZPL 시작 명령


def test_load_nonexistent_template():
    """존재하지 않는 템플릿 로드 테스트"""
    with pytest.raises(TemplateNotFoundError):
        PRNParser("nonexistent.prn")


def test_has_all_variables(parser):
    """모든 변수 존재 확인 테스트"""
    assert parser.has_all_variables() == True


def test_get_missing_variables(parser):
    """누락된 변수 확인 테스트"""
    missing = parser.get_missing_variables()
    assert len(missing) == 0


def test_replace_variables(parser):
    """변수 치환 테스트"""
    zpl = parser.replace_variables(
        date="2025.10.17",
        serial_number="P10DL0S0H3A00B03",
        mac_address="PSAD0CF1327829495",
    )

    # 변수가 치환되었는지 확인
    assert "VAR_DATE" not in zpl
    assert "VAR_SERIALNUMBER" not in zpl
    assert "VAR_2DBARCODE" not in zpl
    assert "VAR_MAC" not in zpl

    # 실제 값이 포함되었는지 확인
    assert "2025.10.17" in zpl
    assert "P10DL0S0H3A00B03" in zpl
    assert "PSAD0CF1327829495" in zpl

    # ZPL 구조가 유지되는지 확인
    assert "^XA" in zpl
    assert "^XZ" in zpl


def test_replace_variables_with_different_data(parser):
    """다른 데이터로 변수 치환 테스트"""
    zpl = parser.replace_variables(
        date="2025.12.31",
        serial_number="W10ML1S1H4A10C99",
        mac_address="TEST1234567890ABC",
    )

    assert "2025.12.31" in zpl
    assert "W10ML1S1H4A10C99" in zpl
    assert "TEST1234567890ABC" in zpl


def test_validate_variables_success(parser):
    """변수 검증 성공 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025.10.17",
        serial_number="P10DL0S0H3A00B03",
        mac_address="PSAD0CF1327829495",
    )

    assert is_valid == True
    assert error_msg == ""


def test_validate_invalid_date(parser):
    """잘못된 날짜 형식 검증 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025-10-17",  # 잘못된 형식 (하이픈)
        serial_number="P10DL0S0H3A00B03",
        mac_address="PSAD0CF1327829495",
    )

    assert is_valid == False
    assert "날짜 형식" in error_msg


def test_validate_invalid_serial_length(parser):
    """잘못된 시리얼 번호 길이 검증 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025.10.17",
        serial_number="P10DL0S0",  # 너무 짧음
        mac_address="PSAD0CF1327829495",
    )

    assert is_valid == False
    assert "16자" in error_msg


def test_validate_invalid_serial_format(parser):
    """잘못된 시리얼 번호 형식 검증 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025.10.17",
        serial_number="1234567890123456",  # 숫자만
        mac_address="PSAD0CF1327829495",
    )

    assert is_valid == False
    assert "시리얼 번호 형식" in error_msg


def test_validate_empty_mac(parser):
    """빈 MAC 주소 검증 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025.10.17",
        serial_number="P10DL0S0H3A00B03",
        mac_address="",
    )

    assert is_valid == False
    assert "비어있습니다" in error_msg


def test_validate_invalid_mac_format(parser):
    """잘못된 MAC 주소 형식 검증 테스트"""
    is_valid, error_msg = parser.validate_variables(
        date="2025.10.17",
        serial_number="P10DL0S0H3A00B03",
        mac_address="psad0cf132782",  # 소문자 포함
    )

    assert is_valid == False
    assert "MAC 주소" in error_msg


def test_replace_with_invalid_variables(parser):
    """유효하지 않은 변수로 치환 시도 테스트"""
    with pytest.raises(InvalidVariableError):
        parser.replace_variables(
            date="invalid-date",
            serial_number="P10DL0S0H3A00B03",
            mac_address="PSAD0CF1327829495",
        )


def test_multiple_replacements(parser):
    """여러 번 치환 테스트"""
    zpl1 = parser.replace_variables(
        "2025.10.17",
        "P10DL0S0H3A00B03",
        "PSAD0CF1327829495",
    )

    zpl2 = parser.replace_variables(
        "2025.10.18",
        "P10DL0S0H3A00B04",
        "PSAD0CF1327829496",
    )

    # 각각 독립적으로 치환되어야 함
    assert "2025.10.17" in zpl1
    assert "2025.10.18" in zpl2
    assert "B03" in zpl1
    assert "B04" in zpl2


def test_parser_repr(parser):
    """repr 테스트"""
    repr_str = repr(parser)
    assert "PRNParser" in repr_str
    assert "PSA_LABEL_ZPL_with_mac_address.prn" in repr_str


def test_template_with_temp_file(tmp_path):
    """임시 템플릿 파일 테스트"""
    # 임시 PRN 파일 생성
    temp_prn = tmp_path / "test.prn"
    temp_prn.write_text(
        "^XA\n"
        "^FDTest Label^FS\n"
        "^FDVAR_DATE^FS\n"
        "^FDVAR_SERIALNUMBER^FS\n"
        "^FDVAR_2DBARCODE^FS\n"
        "^FDVAR_MAC^FS\n"
        "^XZ\n"
    )

    parser = PRNParser(str(temp_prn))
    assert parser.has_all_variables() == True

    zpl = parser.replace_variables(
        "2025.10.17",
        "P10DL0S0H3A00B03",
        "PSAD0CF1327829495",
    )

    assert "VAR_DATE" not in zpl
    assert "2025.10.17" in zpl


def test_template_missing_variables(tmp_path):
    """변수가 누락된 템플릿 테스트"""
    temp_prn = tmp_path / "incomplete.prn"
    temp_prn.write_text(
        "^XA\n"
        "^FDVAR_DATE^FS\n"
        "^FDVAR_SERIALNUMBER^FS\n"
        "^XZ\n"
    )

    parser = PRNParser(str(temp_prn))
    assert parser.has_all_variables() == False

    missing = parser.get_missing_variables()
    assert len(missing) == 2
    assert "VAR_2DBARCODE" in missing
    assert "VAR_MAC" in missing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
