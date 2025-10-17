"""
시리얼 번호 생성기
"""

import re
from typing import Optional
from datetime import datetime

from .exceptions import CounterOverflowError, InvalidSerialNumberError, InvalidCounterError


class SerialNumberGenerator:
    """시리얼 번호 생성 및 관리"""

    # 시리얼 번호 형식 검증 정규식 (총 20자리)
    SERIAL_NUMBER_PATTERN = re.compile(
        r'^[A-Z]\d{2}'  # 모델명: P10 (3자리)
        r'[A-Z]'  # 개발코드: D (1자리)
        r'[A-Z]\d'  # 로봇사양: L0 (2자리)
        r'[A-Z]\d'  # Suite사양: S0 (2자리)
        r'[A-Z]\d'  # HW코드: H3 (2자리)
        r'[A-Z]\d'  # 조립코드: A0 (2자리)
        r'\d'  # Reserved: 0 (1자리)
        r'[A-Z](0[1-9]|1[0-2])'  # 생산일자: C10 (3자리: C=2025년, 10=10월)
        r'\d{4}$'  # 생산순서: 0001 (4자리)
    )

    # 생산일자 코드 형식 검증 (A01 ~ Z12)
    PRODUCTION_DATE_PATTERN = re.compile(r'^[A-Z](0[1-9]|1[0-2])$')

    # 생산순서 형식 검증 (0001 ~ 9999)
    PRODUCTION_SEQUENCE_PATTERN = re.compile(r'^\d{4}$')

    def __init__(
        self,
        model_code: str = "P10",
        dev_code: str = "D",
        robot_spec: str = "L0",
        suite_spec: str = "S0",
        hw_code: str = "H3",
        assembly_code: str = "A0",
        reserved: str = "0",
        production_date: Optional[str] = None,  # None이면 자동으로 현재 날짜
        production_sequence: str = "0001",
    ):
        """
        LOT 정보로 초기화

        Args:
            model_code: 모델명 코드 (3자리, 예: P10)
            dev_code: 개발 코드 (1자리, 예: D)
            robot_spec: 로봇 사양 (2자리, 예: L0)
            suite_spec: Suite 사양 (2자리, 예: S0)
            hw_code: HW 코드 (2자리, 예: H3)
            assembly_code: 조립 코드 (2자리, 예: A0)
            reserved: Reserved (1자리, 예: 0)
            production_date: 생산일자 코드 (3자리, 예: C10 = 2025년 10월, None이면 자동 생성)
            production_sequence: 생산순서 (4자리, 예: 0001)
        """
        self.model_code = model_code
        self.dev_code = dev_code
        self.robot_spec = robot_spec
        self.suite_spec = suite_spec
        self.hw_code = hw_code
        self.assembly_code = assembly_code
        self.reserved = reserved

        # 생산일자가 없으면 현재 날짜로 자동 생성
        if production_date is None:
            production_date = self._generate_current_production_date()

        self._production_date = production_date
        self._production_sequence = production_sequence

        # 초기 검증
        if not self.PRODUCTION_DATE_PATTERN.match(production_date):
            raise InvalidCounterError(f"생산일자 형식 오류: {production_date} (예: C10)")

        if not self.PRODUCTION_SEQUENCE_PATTERN.match(production_sequence):
            raise InvalidCounterError(f"생산순서 형식 오류: {production_sequence} (0001~9999)")

    @staticmethod
    def _generate_current_production_date() -> str:
        """
        현재 날짜를 기반으로 생산일자 코드 생성

        Returns:
            생산일자 코드 (예: C10 = 2025년 10월)
        """
        now = datetime.now()
        year = now.year
        month = now.month

        # 2023년 = A, 2024년 = B, 2025년 = C, ...
        year_code = chr(ord('A') + (year - 2023))

        return f"{year_code}{month:02d}"

    def generate(self) -> str:
        """
        시리얼 번호 생성

        Returns:
            20자리 시리얼 번호

        Example:
            >>> gen = SerialNumberGenerator()
            >>> gen.generate()
            'P10DL0S0H3A00C100001'
        """
        serial_number = (
            f"{self.model_code}"
            f"{self.dev_code}"
            f"{self.robot_spec}"
            f"{self.suite_spec}"
            f"{self.hw_code}"
            f"{self.assembly_code}"
            f"{self.reserved}"
            f"{self._production_date}"
            f"{self._production_sequence}"
        )

        # 생성된 시리얼 번호 검증
        if not self.validate(serial_number):
            raise InvalidSerialNumberError(serial_number, "형식이 올바르지 않습니다")

        return serial_number

    def increment_sequence(self) -> None:
        """
        생산순서 증가

        Example:
            0001 → 0002
            0999 → 1000
            9999 → CounterOverflowError

        Raises:
            CounterOverflowError: 9999 초과
        """
        current_seq = int(self._production_sequence)

        if current_seq >= 9999:
            raise CounterOverflowError()

        self._production_sequence = f"{current_seq + 1:04d}"

    def reset_sequence(self, start: str = "0001") -> None:
        """
        생산순서 리셋

        Args:
            start: 시작 순서 (기본값: 0001)

        Raises:
            InvalidCounterError: 잘못된 형식
        """
        if not self.PRODUCTION_SEQUENCE_PATTERN.match(start):
            raise InvalidCounterError(start)

        self._production_sequence = start

    def set_production_date(self, year_code: str, month: int) -> None:
        """
        생산일자 설정

        Args:
            year_code: 연도 코드 (A=2023, B=2024, C=2025, ...)
            month: 월 (1~12)

        Example:
            >>> gen.set_production_date('C', 10)  # 2025년 10월
        """
        if not year_code.isalpha() or len(year_code) != 1:
            raise InvalidCounterError(f"연도 코드는 알파벳 1자여야 합니다: {year_code}")

        if not (1 <= month <= 12):
            raise InvalidCounterError(f"월은 1~12 사이여야 합니다: {month}")

        self._production_date = f"{year_code.upper()}{month:02d}"

    def set_lot_info(
        self,
        model_code: Optional[str] = None,
        dev_code: Optional[str] = None,
        robot_spec: Optional[str] = None,
        suite_spec: Optional[str] = None,
        hw_code: Optional[str] = None,
        assembly_code: Optional[str] = None,
        reserved: Optional[str] = None,
    ) -> None:
        """
        LOT 정보 설정

        Args:
            model_code: 모델명 코드
            dev_code: 개발 코드
            robot_spec: 로봇 사양
            suite_spec: Suite 사양
            hw_code: HW 코드
            assembly_code: 조립 코드
            reserved: Reserved
        """
        if model_code is not None:
            self.model_code = model_code
        if dev_code is not None:
            self.dev_code = dev_code
        if robot_spec is not None:
            self.robot_spec = robot_spec
        if suite_spec is not None:
            self.suite_spec = suite_spec
        if hw_code is not None:
            self.hw_code = hw_code
        if assembly_code is not None:
            self.assembly_code = assembly_code
        if reserved is not None:
            self.reserved = reserved

    def get_lot_code(self) -> str:
        """
        LOT 코드 반환 (생산일자 + 생산순서 제외)

        Returns:
            13자리 LOT 코드

        Example:
            >>> gen.get_lot_code()
            'P10DL0S0H3A00'
        """
        return (
            f"{self.model_code}"
            f"{self.dev_code}"
            f"{self.robot_spec}"
            f"{self.suite_spec}"
            f"{self.hw_code}"
            f"{self.assembly_code}"
            f"{self.reserved}"
        )

    @staticmethod
    def validate(serial_number: str) -> bool:
        """
        시리얼 번호 형식 검증

        Args:
            serial_number: 시리얼 번호

        Returns:
            유효 여부

        Example:
            >>> SerialNumberGenerator.validate("P10DL0S0H3A00C100001")
            True
            >>> SerialNumberGenerator.validate("INVALID")
            False
        """
        if len(serial_number) != 20:
            return False

        return SerialNumberGenerator.SERIAL_NUMBER_PATTERN.match(serial_number) is not None

    @staticmethod
    def parse_serial_number(serial_number: str) -> dict:
        """
        시리얼 번호를 파싱하여 각 구성 요소 추출

        Args:
            serial_number: 시리얼 번호 (20자)

        Returns:
            {
                'model_code': 'P10',
                'dev_code': 'D',
                'robot_spec': 'L0',
                'suite_spec': 'S0',
                'hw_code': 'H3',
                'assembly_code': 'A0',
                'reserved': '0',
                'production_date': 'C10',
                'production_sequence': '0001',
                'lot_code': 'P10DL0S0H3A00'
            }

        Raises:
            InvalidSerialNumberError: 형식이 올바르지 않음
        """
        if not SerialNumberGenerator.validate(serial_number):
            raise InvalidSerialNumberError(serial_number)

        return {
            'model_code': serial_number[0:3],  # P10
            'dev_code': serial_number[3:4],  # D
            'robot_spec': serial_number[4:6],  # L0
            'suite_spec': serial_number[6:8],  # S0
            'hw_code': serial_number[8:10],  # H3
            'assembly_code': serial_number[10:12],  # A0
            'reserved': serial_number[12:13],  # 0
            'production_date': serial_number[13:16],  # C10
            'production_sequence': serial_number[16:20],  # 0001
            'lot_code': serial_number[0:13],  # P10DL0S0H3A00
        }

    @property
    def production_date(self) -> str:
        """현재 생산일자"""
        return self._production_date

    @property
    def production_sequence(self) -> str:
        """현재 생산순서"""
        return self._production_sequence

    def __repr__(self) -> str:
        return f"SerialNumberGenerator(LOT={self.get_lot_code()}, date={self.production_date}, seq={self.production_sequence})"
