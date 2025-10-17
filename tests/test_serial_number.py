"""
시리얼 번호 생성기 테스트
"""

import pytest
from src.utils.serial_number_generator import SerialNumberGenerator
from src.utils.exceptions import (
    CounterOverflowError,
    InvalidSerialNumberError,
    InvalidCounterError,
)


def test_serial_generation():
    """시리얼 번호 생성 테스트"""
    gen = SerialNumberGenerator()
    sn = gen.generate()

    assert len(sn) == 16
    assert sn == "P10DL0S0H3A00A00"


def test_serial_generation_with_custom_values():
    """커스텀 값으로 시리얼 번호 생성"""
    gen = SerialNumberGenerator(
        model_code="W10",
        dev_code="M",
        robot_spec="L1",
        suite_spec="S1",
        hw_code="H4",
        assembly_code="A1",
        reserved="0",
        counter="B05",
    )

    sn = gen.generate()
    assert sn == "W10ML1S1H4A10B05"


def test_counter_increment():
    """카운터 증가 테스트"""
    gen = SerialNumberGenerator(counter="B03")

    gen.increment_counter()
    assert gen.counter == "B04"

    gen.increment_counter()
    assert gen.counter == "B05"


def test_counter_increment_to_next_letter():
    """카운터가 다음 알파벳으로 넘어가는 테스트"""
    gen = SerialNumberGenerator(counter="B99")

    gen.increment_counter()
    assert gen.counter == "C00"

    gen.increment_counter()
    assert gen.counter == "C01"


def test_counter_overflow():
    """카운터 오버플로우 테스트"""
    gen = SerialNumberGenerator(counter="Z99")

    with pytest.raises(CounterOverflowError):
        gen.increment_counter()


def test_counter_reset():
    """카운터 리셋 테스트"""
    gen = SerialNumberGenerator(counter="C50")

    gen.reset_counter()
    assert gen.counter == "A00"

    gen.reset_counter("B10")
    assert gen.counter == "B10"


def test_invalid_counter():
    """잘못된 카운터 형식 테스트"""
    with pytest.raises(InvalidCounterError):
        SerialNumberGenerator(counter="123")  # 숫자만

    with pytest.raises(InvalidCounterError):
        SerialNumberGenerator(counter="AB1")  # 알파벳 2개

    with pytest.raises(InvalidCounterError):
        SerialNumberGenerator(counter="A1")  # 2자리


def test_set_lot_info():
    """LOT 정보 설정 테스트"""
    gen = SerialNumberGenerator()

    gen.set_lot_info(model_code="W10", robot_spec="L2")
    assert gen.model_code == "W10"
    assert gen.robot_spec == "L2"
    assert gen.dev_code == "D"  # 변경 안 함


def test_get_lot_code():
    """LOT 코드 조회 테스트"""
    gen = SerialNumberGenerator()
    lot_code = gen.get_lot_code()

    assert len(lot_code) == 13
    assert lot_code == "P10DL0S0H3A00"


def test_validate_serial_number():
    """시리얼 번호 검증 테스트"""
    # 유효한 시리얼 번호
    assert SerialNumberGenerator.validate("P10DL0S0H3A00B03") == True
    assert SerialNumberGenerator.validate("W10ML1S1H4A10C50") == True

    # 유효하지 않은 시리얼 번호
    assert SerialNumberGenerator.validate("INVALID") == False
    assert SerialNumberGenerator.validate("P10DL0S0H3A00B0") == False  # 15자리
    assert SerialNumberGenerator.validate("p10dl0s0h3a00b03") == False  # 소문자
    assert SerialNumberGenerator.validate("123DL0S0H3A00B03") == False  # 숫자로 시작


def test_parse_serial_number():
    """시리얼 번호 파싱 테스트"""
    sn = "P10DL0S0H3A00B03"
    parsed = SerialNumberGenerator.parse_serial_number(sn)

    assert parsed['model_code'] == "P10"
    assert parsed['dev_code'] == "D"
    assert parsed['robot_spec'] == "L0"
    assert parsed['suite_spec'] == "S0"
    assert parsed['hw_code'] == "H3"
    assert parsed['assembly_code'] == "A0"
    assert parsed['reserved'] == "0"
    assert parsed['counter'] == "B03"
    assert parsed['lot_code'] == "P10DL0S0H3A00"


def test_parse_invalid_serial_number():
    """잘못된 시리얼 번호 파싱 테스트"""
    with pytest.raises(InvalidSerialNumberError):
        SerialNumberGenerator.parse_serial_number("INVALID")


def test_continuous_generation():
    """연속 생성 테스트"""
    gen = SerialNumberGenerator(counter="A98")

    sn1 = gen.generate()
    assert sn1 == "P10DL0S0H3A00A98"

    gen.increment_counter()
    sn2 = gen.generate()
    assert sn2 == "P10DL0S0H3A00A99"

    gen.increment_counter()
    sn3 = gen.generate()
    assert sn3 == "P10DL0S0H3A00B00"


def test_repr():
    """repr 테스트"""
    gen = SerialNumberGenerator()
    repr_str = repr(gen)

    assert "P10DL0S0H3A00" in repr_str
    assert "A00" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
