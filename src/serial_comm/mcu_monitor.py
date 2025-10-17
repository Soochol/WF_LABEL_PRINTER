"""
MCU 시리얼 모니터 (백그라운드 스레드)
"""

import serial
import time
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal

from .mac_parser import MACParser


class MCUMonitor(QThread):
    """MCU 시리얼 모니터 (백그라운드 스레드)"""

    # 시그널
    mac_received = pyqtSignal(str)  # MAC 주소 수신
    log_received = pyqtSignal(str)  # 로그 라인 수신
    error_occurred = pyqtSignal(str)  # 에러 발생
    connected = pyqtSignal()  # 연결됨
    disconnected = pyqtSignal()  # 연결 끊김

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: int = 1,
    ):
        """
        Args:
            port: 시리얼 포트 (COM3, /dev/ttyUSB0 등)
            baudrate: 보드레이트
            timeout: 읽기 타임아웃 (초)
        """
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self._serial: Optional[serial.Serial] = None
        self._running = False
        self._last_mac: Optional[str] = None

    def run(self) -> None:
        """스레드 메인 루프 (자동 실행)"""
        self._running = True

        try:
            # 시리얼 포트 연결
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            self.connected.emit()

            # 로그 읽기 루프
            while self._running:
                try:
                    if self._serial and self._serial.in_waiting > 0:
                        # 한 줄 읽기
                        line = self._serial.readline().decode('utf-8', errors='ignore').strip()

                        if line:
                            # GUI로 로그 전송
                            self.log_received.emit(line)

                            # MAC 주소 추출
                            mac = MACParser.parse(line)
                            if mac and MACParser.validate(mac):
                                self._last_mac = mac
                                self.mac_received.emit(mac)

                    else:
                        # 데이터가 없으면 짧게 대기
                        time.sleep(0.01)

                except serial.SerialException as e:
                    self.error_occurred.emit(f"시리얼 통신 오류: {e}")
                    break

        except serial.SerialException as e:
            self.error_occurred.emit(f"시리얼 포트 연결 실패: {e}")

        except Exception as e:
            self.error_occurred.emit(f"예상치 못한 오류: {e}")

        finally:
            # 연결 종료
            if self._serial and self._serial.is_open:
                self._serial.close()
            self.disconnected.emit()
            self._running = False

    def stop(self) -> None:
        """모니터링 중지"""
        self._running = False
        self.wait()  # 스레드 종료 대기

    @property
    def is_connected(self) -> bool:
        """연결 상태"""
        return self._serial is not None and self._serial.is_open

    @property
    def last_mac(self) -> Optional[str]:
        """마지막으로 수신한 MAC 주소"""
        return self._last_mac

    def clear_last_mac(self) -> None:
        """마지막 MAC 주소 초기화"""
        self._last_mac = None

    def send_command(self, command: str) -> bool:
        """
        MCU에 명령 전송

        Args:
            command: 명령 문자열

        Returns:
            성공 여부
        """
        if not self.is_connected:
            return False

        try:
            self._serial.write(command.encode('utf-8'))
            return True
        except serial.SerialException:
            return False
