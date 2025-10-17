"""MCU 컨트롤러 - MCU와의 시리얼 통신"""
import serial
import time

class MCUController:
    """MCU 컨트롤러"""

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 30):
        """
        Args:
            port: COM 포트 (예: "COM5")
            baudrate: 통신 속도
            timeout: 타임아웃 (초)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self) -> bool:
        """MCU 연결"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # 연결 안정화 대기
            return True
        except Exception as e:
            print(f"MCU 연결 실패: {e}")
            return False

    def disconnect(self):
        """MCU 연결 해제"""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_mac_address(self) -> str:
        """
        MCU로부터 MAC 주소 읽기

        Returns:
            MAC 주소 (예: "00:1A:2B:3C:4D:5E")
            실패 시 빈 문자열
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("MCU가 연결되지 않았습니다")

        try:
            # 입력 버퍼 비우기
            self.ser.reset_input_buffer()

            # MAC 주소 요청 명령 전송
            # TODO: 실제 MCU 프로토콜에 맞게 수정 필요
            command = b"GET_MAC\r\n"
            self.ser.write(command)

            # 응답 대기
            response = self.ser.readline().decode('utf-8').strip()

            # MAC 주소 검증 (00:1A:2B:3C:4D:5E 형식)
            if self._is_valid_mac(response):
                return response
            else:
                raise ValueError(f"유효하지 않은 MAC 주소 형식: {response}")

        except Exception as e:
            raise RuntimeError(f"MAC 주소 읽기 실패: {str(e)}")

    def _is_valid_mac(self, mac: str) -> bool:
        """MAC 주소 형식 검증"""
        import re
        # 00:1A:2B:3C:4D:5E 형식 검증
        pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        return bool(re.match(pattern, mac))

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.ser is not None and self.ser.is_open
