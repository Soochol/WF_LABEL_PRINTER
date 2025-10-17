"""MCU 백그라운드 모니터 - ESP32 시리얼 모니터링"""
import re
import time
import serial
import serial.tools.list_ports
from PyQt6.QtCore import QThread, pyqtSignal


class MCUMonitor(QThread):
    """MCU 백그라운드 모니터 스레드"""

    # 시그널 정의
    connection_status_changed = pyqtSignal(str, str)  # (status, detail)
    mac_detected = pyqtSignal(str)  # MAC 주소

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 1):
        """
        Args:
            port: COM 포트 (예: "COM5")
            baudrate: 통신 속도
            timeout: 읽기 타임아웃 (초)
        """
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.running = True
        self.ser = None

        # MAC 주소 패턴: device id: PSAD0CF1327829495
        self.mac_pattern = re.compile(r'device id:\s*(PSA[A-Fa-f0-9]{13})')

    def run(self):
        """백그라운드 모니터링 실행"""
        while self.running:
            try:
                # 시리얼 포트 연결 시도
                if not self.ser or not self.ser.is_open:
                    self._connect()

                # 연결되었으면 데이터 읽기
                if self.ser and self.ser.is_open:
                    self._read_data()

            except Exception as e:
                print(f"MCU 모니터 오류: {e}")
                self._handle_error()

            # 재연결 대기
            time.sleep(0.1)

    def _connect(self):
        """시리얼 포트 연결"""
        try:
            # 연결 시도 중 상태
            self.connection_status_changed.emit("reconnecting", self.port)

            # 포트가 존재하는지 확인
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if self.port not in available_ports:
                raise RuntimeError(f"포트 {self.port}를 찾을 수 없습니다")

            # 시리얼 포트 열기
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )

            # 연결 성공
            self.connection_status_changed.emit("connected", self.port)
            print(f"✓ MCU 연결됨: {self.port}")

        except Exception as e:
            # 연결 실패
            self.connection_status_changed.emit("disconnected", "")
            print(f"✗ MCU 연결 실패: {e}")
            # 5초 대기 후 재시도
            time.sleep(5)

    def _read_data(self):
        """시리얼 데이터 읽기"""
        try:
            if self.ser.in_waiting > 0:
                # 한 줄 읽기
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()

                if line:
                    # MAC 주소 패턴 검색
                    match = self.mac_pattern.search(line)
                    if match:
                        mac_address = match.group(1)
                        print(f"✓ MAC 감지: {mac_address}")
                        self.mac_detected.emit(mac_address)

        except serial.SerialException as e:
            # 시리얼 통신 오류 (연결 끊김 등)
            print(f"시리얼 통신 오류: {e}")
            self._close()
            self.connection_status_changed.emit("disconnected", "")

        except Exception as e:
            print(f"데이터 읽기 오류: {e}")

    def _handle_error(self):
        """에러 처리"""
        self._close()
        self.connection_status_changed.emit("reconnecting", self.port)
        time.sleep(5)  # 5초 대기 후 재시도

    def _close(self):
        """시리얼 포트 닫기"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.ser = None

    def stop(self):
        """모니터링 중지"""
        self.running = False
        self._close()
        self.wait()  # 스레드 종료 대기
