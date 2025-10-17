"""
유틸리티 관련 예외 클래스
"""


class CounterOverflowError(Exception):
    """카운터 오버플로우 (Z99 초과)"""
    def __init__(self):
        super().__init__("생산순서 카운터가 최대값(Z99)을 초과했습니다.")


class InvalidSerialNumberError(Exception):
    """유효하지 않은 시리얼 번호"""
    def __init__(self, serial_number: str, reason: str = ""):
        self.serial_number = serial_number
        message = f"유효하지 않은 시리얼 번호: {serial_number}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class InvalidCounterError(Exception):
    """유효하지 않은 카운터 형식"""
    def __init__(self, counter: str):
        self.counter = counter
        super().__init__(f"유효하지 않은 카운터 형식: {counter}")
