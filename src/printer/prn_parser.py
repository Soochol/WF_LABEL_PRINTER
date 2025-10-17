"""
PRN 파일 파서 및 변수 치환
"""

import re
from pathlib import Path
from typing import Optional, Tuple

from .exceptions import TemplateNotFoundError, InvalidVariableError


class PRNParser:
    """PRN 파일 파서 및 변수 치환"""

    # 변수 이름
    VAR_DATE = "VAR_DATE"
    VAR_SERIALNUMBER = "VAR_SERIALNUMBER"
    VAR_2DBARCODE = "VAR_2DBARCODE"
    VAR_MAC = "VAR_MAC"

    # 날짜 형식 검증 (YYYY.MM.DD)
    DATE_PATTERN = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')

    # 시리얼 번호 형식 검증 (20자)
    SERIAL_PATTERN = re.compile(
        r'^[A-Z]\d{2}'  # 모델명: P10
        r'[A-Z]'  # 개발코드: D
        r'[A-Z]\d'  # 로봇사양: L0
        r'[A-Z]\d'  # Suite사양: S0
        r'[A-Z]\d'  # HW코드: H3
        r'[A-Z]\d'  # 조립코드: A0
        r'\d'  # Reserved: 0
        r'[A-Z](0[1-9]|1[0-2])'  # 생산일자: C10
        r'\d{4}$'  # 생산순서: 0001
    )

    # MAC 주소 형식 검증 (영문 대문자 + 숫자)
    MAC_PATTERN = re.compile(r'^[A-Z0-9]+$')

    def __init__(self, template_path: str):
        """
        Args:
            template_path: PRN 템플릿 파일 경로

        Raises:
            TemplateNotFoundError: 템플릿 파일이 없음
        """
        self.template_path = template_path
        self._template_content: Optional[str] = None
        self.load_template(template_path)

    def load_template(self, template_path: str) -> None:
        """
        템플릿 파일 로드

        Args:
            template_path: PRN 템플릿 파일 경로

        Raises:
            TemplateNotFoundError: 템플릿 파일이 없음
        """
        path = Path(template_path)

        if not path.exists():
            raise TemplateNotFoundError(template_path)

        with open(path, 'r', encoding='utf-8-sig') as f:
            self._template_content = f.read()

        self.template_path = template_path

    def replace_variables(
        self,
        date: str,
        serial_number: str,
        mac_address: str,
    ) -> str:
        """
        변수 치환하여 ZPL 명령 생성

        Args:
            date: 날짜 (YYYY.MM.DD)
            serial_number: 시리얼 번호 (20자)
            mac_address: MAC 주소

        Returns:
            치환된 ZPL 명령 문자열

        Raises:
            InvalidVariableError: 변수 값이 유효하지 않음

        Example:
            >>> parser.replace_variables(
                "2025.10.17",
                "P10DL0S0H3A00B03",
                "PSAD0CF1327829495"
            )
        """
        # 변수 검증
        is_valid, error_msg = self.validate_variables(date, serial_number, mac_address)
        if not is_valid:
            raise InvalidVariableError("variables", "", error_msg)

        if self._template_content is None:
            raise TemplateNotFoundError(self.template_path)

        # 변수 치환
        zpl = self._template_content
        zpl = zpl.replace(self.VAR_DATE, date)
        zpl = zpl.replace(self.VAR_SERIALNUMBER, serial_number)
        zpl = zpl.replace(self.VAR_2DBARCODE, serial_number)  # 2D 바코드는 시리얼 번호와 동일
        zpl = zpl.replace(self.VAR_MAC, mac_address)

        # ^FH\ 문제 해결: 바코드 데이터 바로 앞의 ^FH\를 제거
        # ZPL의 ^FH (Field Hex) 명령이 데이터를 잘못 해석하는 것을 방지
        # 예: ^FH\^FDPSAD0CF... -> ^FDLA,PSAD0CF... (Alphanumeric mode)

        # 2D 바코드 (QR Code) 처리
        # ^BQ 명령어 다음 줄의 ^FH\^FD를 ^FDLA,로 변경
        # 예: ^BQN,2,3 다음 줄 ^FH\^FD{data}^FS -> ^FDLA,{data}^FS
        zpl = re.sub(
            r'(\^BQ[^\n]+\n)\^FH\\\^FD',
            r'\1^FDLA,',
            zpl
        )

        # 1D 바코드 (Code 128) 처리
        # ^BC 명령어 다음 줄의 ^FH\^FD를 그냥 ^FD로 변경
        # Code 128은 자동으로 최적 subset을 선택하므로 prefix 불필요
        zpl = re.sub(
            r'(\^BC[^\n]+\n)\^FH\\\^FD',
            r'\1^FD',
            zpl
        )

        # 일반 텍스트 필드의 ^FH\는 유지 (^CI28과 함께 사용되는 경우)
        # ^FH\^CI28은 한글/특수문자 처리를 위한 것이므로 건드리지 않음

        return zpl

    def validate_variables(
        self,
        date: str,
        serial_number: str,
        mac_address: str,
    ) -> Tuple[bool, str]:
        """
        변수 검증

        Args:
            date: 날짜
            serial_number: 시리얼 번호
            mac_address: MAC 주소

        Returns:
            (검증 결과, 에러 메시지)
        """
        # 날짜 검증
        if not self.DATE_PATTERN.match(date):
            return False, f"날짜 형식이 올바르지 않습니다: {date} (YYYY.MM.DD 형식이어야 합니다)"

        # 시리얼 번호 검증
        if len(serial_number) != 20:
            return False, f"시리얼 번호는 20자여야 합니다: {serial_number} (길이: {len(serial_number)})"

        if not self.SERIAL_PATTERN.match(serial_number):
            return False, f"시리얼 번호 형식이 올바르지 않습니다: {serial_number}"

        # MAC 주소 검증
        if not mac_address:
            return False, "MAC 주소가 비어있습니다"

        if not self.MAC_PATTERN.match(mac_address):
            return False, f"MAC 주소는 영문 대문자와 숫자만 포함해야 합니다: {mac_address}"

        return True, ""

    @property
    def template(self) -> str:
        """원본 템플릿"""
        return self._template_content or ""

    def has_all_variables(self) -> bool:
        """
        템플릿에 모든 필수 변수가 포함되어 있는지 확인

        Returns:
            모든 변수 포함 여부
        """
        if self._template_content is None:
            return False

        return (
            self.VAR_DATE in self._template_content
            and self.VAR_SERIALNUMBER in self._template_content
            and self.VAR_2DBARCODE in self._template_content
            and self.VAR_MAC in self._template_content
        )

    def get_missing_variables(self) -> list:
        """
        템플릿에서 누락된 변수 목록 반환

        Returns:
            누락된 변수 이름 리스트
        """
        if self._template_content is None:
            return [self.VAR_DATE, self.VAR_SERIALNUMBER, self.VAR_2DBARCODE, self.VAR_MAC]

        missing = []
        if self.VAR_DATE not in self._template_content:
            missing.append(self.VAR_DATE)
        if self.VAR_SERIALNUMBER not in self._template_content:
            missing.append(self.VAR_SERIALNUMBER)
        if self.VAR_2DBARCODE not in self._template_content:
            missing.append(self.VAR_2DBARCODE)
        if self.VAR_MAC not in self._template_content:
            missing.append(self.VAR_MAC)

        return missing

    def __repr__(self) -> str:
        return f"PRNParser(template='{self.template_path}')"
