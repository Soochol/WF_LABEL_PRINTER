"""
MCU 시리얼 통신 모니터
실시간 데이터 수신 및 MAC 주소 파싱
"""

import serial
import serial.tools.list_ports
import threading
import re
from typing import Optional, Callable, List
from queue import Queue
import time


class SerialMonitor:
    """
    시리얼 모니터 클래스

    MCU와 시리얼 통신을 통해 데이터를 수신하고
    MAC 주소를 자동으로 파싱합니다.
    """

    def __init__(self, baudrate: int = 115200):
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_running = False

        # 콜백 함수들
        self.on_data_received: Optional[Callable[[str], None]] = None
        self.on_mac_detected: Optional[Callable[[str], None]] = None
        self.on_connection_changed: Optional[Callable[[bool], None]] = None

        # 수신 스레드
        self.receive_thread: Optional[threading.Thread] = None

        # MAC 주소 패턴 (예: PSAD0CF1327829495)
        self.mac_pattern = re.compile(r'PSA[0-9A-F]{14}', re.IGNORECASE)

    @staticmethod
    def list_available_ports() -> List[str]:
        """사용 가능한 시리얼 포트 목록 반환"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self, port: str) -> bool:
        """
        시리얼 포트 연결

        Args:
            port: 포트 이름 (예: "COM3")

        Returns:
            연결 성공 여부
        """
        try:
            # 이미 연결되어 있으면 먼저 연결 해제
            if self.is_connected:
                self.disconnect()

            # 시리얼 포트 열기
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )

            self.is_connected = True
            self.is_running = True

            # 수신 스레드 시작
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            # 연결 상태 콜백
            if self.on_connection_changed:
                self.on_connection_changed(True)

            return True

        except Exception as e:
            print(f"Serial connection error: {e}")
            self.is_connected = False

            # 연결 실패 콜백
            if self.on_connection_changed:
                self.on_connection_changed(False)

            return False

    def disconnect(self):
        """시리얼 포트 연결 해제"""
        self.is_running = False

        # 스레드 종료 대기
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2)

        # 포트 닫기
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except Exception as e:
                print(f"Error closing serial port: {e}")

        self.is_connected = False
        self.serial_port = None

        # 연결 상태 콜백
        if self.on_connection_changed:
            self.on_connection_changed(False)

    def send(self, data: str):
        """
        데이터 전송

        Args:
            data: 전송할 문자열
        """
        if not self.is_connected or not self.serial_port:
            return

        try:
            # 개행 문자 추가
            if not data.endswith('\n'):
                data += '\n'

            self.serial_port.write(data.encode('utf-8'))

        except Exception as e:
            print(f"Serial send error: {e}")

    def _receive_loop(self):
        """수신 루프 (별도 스레드에서 실행)"""
        buffer = ""

        while self.is_running and self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    # 데이터 읽기
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)

                    # UTF-8 디코딩 시도
                    try:
                        decoded_data = raw_data.decode('utf-8', errors='replace')
                    except:
                        decoded_data = raw_data.decode('latin-1', errors='replace')

                    buffer += decoded_data

                    # 라인 단위로 처리
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()

                        if line:
                            # 데이터 수신 콜백
                            if self.on_data_received:
                                self.on_data_received(line)

                            # MAC 주소 감지
                            self._check_mac_address(line)

                else:
                    # 데이터 없을 때 짧은 대기
                    time.sleep(0.01)

            except serial.SerialException as e:
                print(f"Serial receive error: {e}")
                self.disconnect()
                break
            except Exception as e:
                print(f"Unexpected error in receive loop: {e}")
                time.sleep(0.1)

    def _check_mac_address(self, line: str):
        """
        라인에서 MAC 주소 패턴 검사

        Args:
            line: 검사할 문자열
        """
        match = self.mac_pattern.search(line)
        if match:
            mac_address = match.group(0).upper()

            # MAC 감지 콜백
            if self.on_mac_detected:
                self.on_mac_detected(mac_address)

    def auto_connect(self) -> Optional[str]:
        """
        자동으로 사용 가능한 포트에 연결 시도

        Returns:
            연결된 포트 이름 또는 None
        """
        available_ports = self.list_available_ports()

        for port in available_ports:
            if self.connect(port):
                return port

        return None

    def __del__(self):
        """소멸자 - 연결 정리"""
        self.disconnect()
