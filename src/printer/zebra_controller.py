"""
Zebra USB 프린터 제어
"""

import usb.core
import usb.util
from typing import Optional, Dict

from .exceptions import (
    PrinterNotFoundError,
    PrinterNotConnectedError,
    PrinterCommunicationError,
)
from .printer_discovery import PrinterDiscovery


class ZebraController:
    """Zebra USB 프린터 제어 클래스"""

    # Zebra VID
    ZEBRA_VENDOR_ID = 0x0A5F

    # USB 엔드포인트
    ENDPOINT_OUT = 0x01  # 출력 엔드포인트 (프린터로 데이터 전송)

    def __init__(self, vendor_id: int = ZEBRA_VENDOR_ID, product_id: Optional[int] = None):
        """
        Args:
            vendor_id: Zebra VID (기본값: 0x0A5F)
            product_id: 프린터 PID (None이면 자동 검색)
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device: Optional[usb.core.Device] = None
        self.endpoint_out: Optional[int] = None

    def connect(self) -> bool:
        """
        프린터 연결

        Returns:
            성공 여부

        Raises:
            PrinterNotFoundError: 프린터를 찾을 수 없음
            PrinterCommunicationError: USB 연결 오류
        """
        try:
            # 프린터 검색
            if self.product_id:
                self.device = usb.core.find(
                    idVendor=self.vendor_id,
                    idProduct=self.product_id
                )
            else:
                # PID가 없으면 VID만으로 검색 (첫 번째 장치 선택)
                self.device = usb.core.find(idVendor=self.vendor_id)

            if self.device is None:
                raise PrinterNotFoundError()

            # 커널 드라이버가 활성화되어 있으면 분리
            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                except Exception:
                    pass  # Windows에서는 필요없음

            # 설정 및 인터페이스 설정
            self.device.set_configuration()

            # 출력 엔드포인트 찾기
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]

            # Bulk OUT 엔드포인트 찾기
            ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )

            if ep_out is None:
                raise PrinterCommunicationError("출력 엔드포인트를 찾을 수 없습니다")

            self.endpoint_out = ep_out.bEndpointAddress

            return True

        except usb.core.USBError as e:
            raise PrinterCommunicationError(f"USB 연결 오류: {e}")

    def disconnect(self) -> None:
        """프린터 연결 해제"""
        if self.device:
            try:
                usb.util.dispose_resources(self.device)
            except Exception:
                pass
            self.device = None
            self.endpoint_out = None

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
        if not self.is_connected:
            raise PrinterNotConnectedError()

        try:
            # ZPL 명령을 바이트로 변환
            data = zpl_commands.encode('utf-8')

            # 프린터로 전송
            self.device.write(self.endpoint_out, data)

            return True

        except usb.core.USBError as e:
            raise PrinterCommunicationError(f"데이터 전송 오류: {e}")

    def get_status(self) -> Dict:
        """
        프린터 상태 조회

        Returns:
            {
                'connected': bool,
                'ready': bool,
                'error': str or None
            }
        """
        status = {
            'connected': self.is_connected,
            'ready': self.is_connected,
            'error': None
        }

        if not self.is_connected:
            status['ready'] = False
            status['error'] = "프린터가 연결되지 않았습니다"

        return status

    def test_print(self, test_text: str = "TEST LABEL") -> bool:
        """
        테스트 라벨 출력

        Args:
            test_text: 테스트 텍스트

        Returns:
            성공 여부
        """
        # 간단한 테스트 ZPL 명령
        zpl = f"""
^XA
^FO50,50^A0N,50,50^FD{test_text}^FS
^FO50,120^A0N,30,30^FDTest Print - Zebra Printer^FS
^FO50,160^A0N,30,30^FDWITHFORCE INC.^FS
^XZ
"""
        return self.send_zpl(zpl)

    @property
    def is_connected(self) -> bool:
        """프린터 연결 상태"""
        return self.device is not None

    def __repr__(self) -> str:
        status = "Connected" if self.is_connected else "Disconnected"
        return f"ZebraController(VID=0x{self.vendor_id:04X}, PID=0x{self.product_id:04X if self.product_id else 0:04X}, {status})"

    def __enter__(self):
        """Context manager 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.disconnect()
