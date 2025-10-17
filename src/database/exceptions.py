"""
데이터베이스 관련 예외 클래스
"""


class DatabaseError(Exception):
    """데이터베이스 관련 기본 예외"""
    pass


class DuplicateSerialNumberError(DatabaseError):
    """중복된 시리얼 번호"""
    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        super().__init__(f"중복된 시리얼 번호: {serial_number}")


class LOTConfigNotFoundError(DatabaseError):
    """LOT 설정을 찾을 수 없음"""
    def __init__(self):
        super().__init__("LOT 설정이 초기화되지 않았습니다.")


class ConfigKeyNotFoundError(DatabaseError):
    """설정 키를 찾을 수 없음"""
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"설정 키를 찾을 수 없음: {key}")
