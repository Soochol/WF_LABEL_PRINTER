"""
프린터 관련 예외 클래스
"""


class PrinterError(Exception):
    """프린터 관련 기본 예외"""
    pass


class PrinterNotFoundError(PrinterError):
    """프린터를 찾을 수 없음"""
    def __init__(self):
        super().__init__("Zebra 프린터를 찾을 수 없습니다.")


class PrinterNotConnectedError(PrinterError):
    """프린터가 연결되지 않음"""
    def __init__(self):
        super().__init__("프린터가 연결되지 않았습니다.")


class PrinterCommunicationError(PrinterError):
    """프린터 통신 오류"""
    def __init__(self, message: str):
        super().__init__(f"프린터 통신 오류: {message}")


class TemplateNotFoundError(PrinterError):
    """PRN 템플릿 파일을 찾을 수 없음"""
    def __init__(self, template_path: str):
        self.template_path = template_path
        super().__init__(f"PRN 템플릿 파일을 찾을 수 없습니다: {template_path}")


class InvalidVariableError(PrinterError):
    """유효하지 않은 변수 값"""
    def __init__(self, variable_name: str, value: str, reason: str):
        self.variable_name = variable_name
        self.value = value
        self.reason = reason
        super().__init__(f"유효하지 않은 변수 값: {variable_name}={value} ({reason})")
