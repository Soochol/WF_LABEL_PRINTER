# API 설계 문서

## 모듈 구조

```
src/
├── printer/
│   ├── zebra_controller.py       # Zebra 프린터 제어
│   ├── prn_parser.py              # PRN 파일 파서
│   └── printer_discovery.py       # 프린터 검색
├── serial_comm/
│   ├── mcu_monitor.py             # MCU 시리얼 모니터
│   └── mac_parser.py              # MAC 주소 파서
├── database/
│   ├── db_manager.py              # DB 관리자
│   └── models.py                  # 데이터 모델
├── gui/
│   └── (PyQt6 위젯들)
└── utils/
    ├── serial_number_generator.py # 시리얼 번호 생성기
    ├── config_manager.py          # 설정 관리자
    └── logger.py                  # 로거
```

---

## 1. printer/zebra_controller.py

### ZebraController 클래스

```python
class ZebraController:
    """Zebra USB 프린터 제어 클래스"""

    def __init__(self, vendor_id: int = 0x0A5F, product_id: int = None):
        """
        Args:
            vendor_id: Zebra VID (기본값: 0x0A5F)
            product_id: 프린터 PID (None이면 자동 검색)
        """

    def connect(self) -> bool:
        """
        프린터 연결

        Returns:
            성공 여부

        Raises:
            PrinterNotFoundError: 프린터를 찾을 수 없음
            USBError: USB 연결 오류
        """

    def disconnect(self) -> None:
        """프린터 연결 해제"""

    def send_zpl(self, zpl_commands: str) -> bool:
        """
        ZPL 명령 전송

        Args:
            zpl_commands: ZPL 명령 문자열

        Returns:
            성공 여부

        Raises:
            PrinterNotConnectedError: 프린터가 연결되지 않음
            PrinterCommunicationError: 통신 오류
        """

    def get_status(self) -> dict:
        """
        프린터 상태 조회

        Returns:
            {
                'connected': bool,
                'ready': bool,
                'paper_out': bool,
                'error': str or None
            }
        """

    def test_print(self) -> bool:
        """
        테스트 라벨 출력

        Returns:
            성공 여부
        """

    @property
    def is_connected(self) -> bool:
        """프린터 연결 상태"""
```

---

## 2. printer/prn_parser.py

### PRNParser 클래스

```python
class PRNParser:
    """PRN 파일 파서 및 변수 치환"""

    def __init__(self, template_path: str):
        """
        Args:
            template_path: PRN 템플릿 파일 경로

        Raises:
            FileNotFoundError: 템플릿 파일이 없음
        """

    def load_template(self, template_path: str) -> None:
        """
        템플릿 파일 로드

        Args:
            template_path: PRN 템플릿 파일 경로
        """

    def replace_variables(
        self,
        date: str,
        serial_number: str,
        mac_address: str
    ) -> str:
        """
        변수 치환하여 ZPL 명령 생성

        Args:
            date: 날짜 (YYYY.MM.DD)
            serial_number: 시리얼 번호 (16자)
            mac_address: MAC 주소

        Returns:
            치환된 ZPL 명령 문자열

        Example:
            >>> parser.replace_variables(
                "2025.10.17",
                "P10DL0S0H3A00B03",
                "PSAD0CF1327829495"
            )
        """

    def validate_variables(
        self,
        date: str,
        serial_number: str,
        mac_address: str
    ) -> tuple[bool, str]:
        """
        변수 검증

        Returns:
            (검증 결과, 에러 메시지)
        """

    @property
    def template(self) -> str:
        """원본 템플릿"""
```

---

## 3. printer/printer_discovery.py

### PrinterDiscovery 클래스

```python
class PrinterDiscovery:
    """USB 프린터 검색"""

    @staticmethod
    def find_zebra_printers() -> list[dict]:
        """
        Zebra 프린터 검색

        Returns:
            [
                {
                    'vendor_id': int,
                    'product_id': int,
                    'manufacturer': str,
                    'product': str,
                    'serial': str
                },
                ...
            ]
        """

    @staticmethod
    def find_printer_by_vid_pid(vendor_id: int, product_id: int) -> dict | None:
        """
        VID/PID로 프린터 검색

        Returns:
            프린터 정보 dict 또는 None
        """
```

---

## 4. serial_comm/mcu_monitor.py

### MCUMonitor 클래스

```python
from PyQt6.QtCore import QThread, pyqtSignal

class MCUMonitor(QThread):
    """MCU 시리얼 모니터 (백그라운드 스레드)"""

    # 시그널
    mac_received = pyqtSignal(str)      # MAC 주소 수신
    log_received = pyqtSignal(str)       # 로그 라인 수신
    error_occurred = pyqtSignal(str)     # 에러 발생
    connected = pyqtSignal()             # 연결됨
    disconnected = pyqtSignal()          # 연결 끊김

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: int = 30
    ):
        """
        Args:
            port: 시리얼 포트 (COM3, /dev/ttyUSB0 등)
            baudrate: 보드레이트
            timeout: MAC 수신 타임아웃 (초)
        """

    def run(self) -> None:
        """스레드 메인 루프 (자동 실행)"""

    def stop(self) -> None:
        """모니터링 중지"""

    @property
    def is_connected(self) -> bool:
        """연결 상태"""

    @property
    def last_mac(self) -> str | None:
        """마지막으로 수신한 MAC 주소"""
```

---

## 5. serial_comm/mac_parser.py

### MACParser 클래스

```python
class MACParser:
    """MAC 주소 파서"""

    # 정규식 패턴: "device id: PSAD0CF1327829495"
    PATTERN = re.compile(r'device id:\s*([A-Z0-9]+)')

    @staticmethod
    def parse(log_line: str) -> str | None:
        """
        로그 라인에서 MAC 주소 추출

        Args:
            log_line: 로그 라인 문자열

        Returns:
            MAC 주소 또는 None

        Example:
            >>> MACParser.parse("device id: PSAD0CF1327829495")
            'PSAD0CF1327829495'
        """

    @staticmethod
    def validate(mac_address: str) -> bool:
        """
        MAC 주소 형식 검증

        Args:
            mac_address: MAC 주소 문자열

        Returns:
            유효 여부
        """
```

---

## 6. utils/serial_number_generator.py

### SerialNumberGenerator 클래스

```python
class SerialNumberGenerator:
    """시리얼 번호 생성 및 관리"""

    def __init__(
        self,
        model_code: str = "P10",
        dev_code: str = "D",
        robot_spec: str = "L0",
        suite_spec: str = "S0",
        hw_code: str = "H3",
        assembly_code: str = "A0",
        reserved: str = "0",
        counter: str = "A00"
    ):
        """LOT 정보로 초기화"""

    def generate(self) -> str:
        """
        시리얼 번호 생성

        Returns:
            16자리 시리얼 번호

        Example:
            >>> gen.generate()
            'P10DL0S0H3A00B03'
        """

    def increment_counter(self) -> None:
        """
        생산순서 카운터 증가

        Example:
            B03 → B04
            B99 → C00

        Raises:
            CounterOverflowError: Z99 초과
        """

    def reset_counter(self, start: str = "A00") -> None:
        """
        카운터 리셋

        Args:
            start: 시작 카운터 (기본값: A00)
        """

    def set_lot_info(self, **kwargs) -> None:
        """
        LOT 정보 설정

        Args:
            model_code: 모델명 코드
            dev_code: 개발 코드
            robot_spec: 로봇 사양
            ... (기타 LOT 구성 요소)
        """

    def get_lot_code(self) -> str:
        """
        LOT 코드 반환 (생산순서 제외)

        Returns:
            13자리 LOT 코드

        Example:
            >>> gen.get_lot_code()
            'P10DL0S0H3A00'
        """

    @staticmethod
    def validate(serial_number: str) -> bool:
        """
        시리얼 번호 형식 검증

        Returns:
            유효 여부
        """

    @property
    def counter(self) -> str:
        """현재 카운터"""
```

---

## 7. database/db_manager.py

### DBManager 클래스

```python
class DBManager:
    """데이터베이스 관리자"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: SQLite DB 파일 경로
        """

    def initialize(self) -> None:
        """
        데이터베이스 초기화
        - 테이블 생성
        - 인덱스 생성
        - 초기 데이터 삽입
        """

    def save_print_history(
        self,
        serial_number: str,
        mac_address: str,
        print_date: str,
        status: str,
        error_message: str = None,
        prn_template: str = "PSA_LABEL_ZPL_with_mac_address.prn"
    ) -> int:
        """
        출력 이력 저장

        Returns:
            삽입된 레코드 ID

        Raises:
            DuplicateSerialNumberError: 중복된 시리얼 번호
        """

    def get_print_history(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from: str = None,
        date_to: str = None,
        serial_number: str = None
    ) -> list[dict]:
        """
        출력 이력 조회

        Returns:
            이력 레코드 리스트
        """

    def get_lot_config(self) -> dict:
        """
        LOT 설정 조회

        Returns:
            {
                'model_code': str,
                'dev_code': str,
                ...
            }
        """

    def update_lot_config(self, **kwargs) -> None:
        """
        LOT 설정 업데이트

        Args:
            model_code: 모델명 코드
            dev_code: 개발 코드
            ... (업데이트할 필드)
        """

    def increment_counter(self, new_counter: str) -> None:
        """
        생산순서 카운터 업데이트

        Args:
            new_counter: 새 카운터 값
        """

    def get_config(self, key: str) -> str | None:
        """
        앱 설정 조회

        Returns:
            설정 값 또는 None
        """

    def set_config(self, key: str, value: str) -> None:
        """앱 설정 저장"""

    def get_code_master(self, code_type: str) -> list[dict]:
        """
        코드 마스터 조회

        Args:
            code_type: 코드 타입 (model_code, dev_code 등)

        Returns:
            [
                {'code_value': 'P10', 'code_name': 'PSP 1.0'},
                ...
            ]
        """

    def backup(self, backup_path: str) -> None:
        """데이터베이스 백업"""

    def close(self) -> None:
        """데이터베이스 연결 종료"""
```

---

## 8. utils/config_manager.py

### ConfigManager 클래스

```python
class ConfigManager:
    """YAML 설정 파일 관리자"""

    def __init__(self, config_path: str = "./config.yaml"):
        """
        Args:
            config_path: 설정 파일 경로
        """

    def load(self) -> dict:
        """설정 로드"""

    def save(self, config: dict) -> None:
        """설정 저장"""

    def get(self, key: str, default=None):
        """
        설정 값 조회

        Args:
            key: 키 (점 표기법 지원: "printer.vendor_id")
            default: 기본값

        Example:
            >>> config.get("printer.vendor_id")
            0x0A5F
        """

    def set(self, key: str, value) -> None:
        """설정 값 저장"""
```

---

## 9. utils/logger.py

### 로거 설정

```python
def setup_logger(
    name: str = "label_printer",
    level: str = "INFO",
    log_file: str = "./logs/app.log"
) -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨
        log_file: 로그 파일 경로

    Returns:
        로거 인스턴스
    """
```

---

## 워크플로우 예시

### 라벨 출력 플로우

```python
# 1. 초기화
config = ConfigManager()
db = DBManager("./data/label_printer.db")
printer = ZebraController()
parser = PRNParser(config.get("printer.prn_template"))
sn_gen = SerialNumberGenerator(**db.get_lot_config())

# 2. 프린터 연결
if not printer.connect():
    raise Exception("프린터 연결 실패")

# 3. MCU 모니터 시작
mcu = MCUMonitor(config.get("serial.port"))
mac_address = None

def on_mac_received(mac: str):
    global mac_address
    mac_address = mac

mcu.mac_received.connect(on_mac_received)
mcu.start()

# 4. MAC 수신 대기
while mac_address is None:
    time.sleep(0.1)

# 5. 시리얼 번호 생성
serial_number = sn_gen.generate()
date = datetime.now().strftime("%Y.%m.%d")

# 6. ZPL 생성
zpl = parser.replace_variables(date, serial_number, mac_address)

# 7. 출력
try:
    printer.send_zpl(zpl)
    db.save_print_history(serial_number, mac_address, date, "success")
    sn_gen.increment_counter()
    db.increment_counter(sn_gen.counter)
except Exception as e:
    db.save_print_history(
        serial_number, mac_address, date, "failed", str(e)
    )
    raise

# 8. 정리
mcu.stop()
printer.disconnect()
db.close()
```

---

## 에러 클래스 정의

```python
# printer/exceptions.py
class PrinterError(Exception):
    """프린터 관련 기본 예외"""

class PrinterNotFoundError(PrinterError):
    """프린터를 찾을 수 없음"""

class PrinterNotConnectedError(PrinterError):
    """프린터가 연결되지 않음"""

class PrinterCommunicationError(PrinterError):
    """프린터 통신 오류"""

# database/exceptions.py
class DatabaseError(Exception):
    """데이터베이스 관련 기본 예외"""

class DuplicateSerialNumberError(DatabaseError):
    """중복된 시리얼 번호"""

# utils/exceptions.py
class CounterOverflowError(Exception):
    """카운터 오버플로우 (Z99 초과)"""

class InvalidSerialNumberError(Exception):
    """유효하지 않은 시리얼 번호"""
```
