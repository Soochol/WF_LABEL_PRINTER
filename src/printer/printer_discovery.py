"""
USB 프린터 검색
"""

from typing import List, Dict, Optional

import usb.core
import usb.util


class PrinterDiscovery:
    """USB 프린터 검색"""

    # Zebra VID (Vendor ID)
    ZEBRA_VENDOR_ID = 0x0A5F

    @staticmethod
    def _get_libusb_backend():
        """
        libusb backend 가져오기 (자동으로 libusb-package 사용)

        Returns:
            libusb backend 객체

        Raises:
            RuntimeError: backend를 찾을 수 없는 경우
        """
        # 1. libusb-package 사용 (자동으로 DLL 경로 처리)
        try:
            import libusb_package
            backend = libusb_package.get_libusb1_backend()
            if backend is not None:
                return backend
        except ImportError:
            pass

        # 2. 기본 경로에서 backend 찾기 시도
        try:
            import usb.backend.libusb1
            backend = usb.backend.libusb1.get_backend()
            if backend is not None:
                return backend
        except Exception:
            pass

        # 3. 모든 방법 실패 시 에러 메시지
        error_msg = """
╔═══════════════════════════════════════════════════════════════════╗
║                   USB Backend 설치 필요                            ║
╚═══════════════════════════════════════════════════════════════════╝

PyUSB가 USB 장치와 통신하려면 libusb backend가 필요합니다.

【Windows 설치 방법】

1. libusb-package 설치 (권장):
   > uv pip install libusb-package

2. 수동 설치:
   - https://github.com/libusb/libusb/releases 에서 다운로드
   - libusb-1.0.dll 파일을 다음 위치에 복사:
     • C:\\Windows\\System32\\ (64-bit)
     • 또는 프로젝트 폴더

3. 설치 후 터미널 재시작

현재 상태: libusb backend를 찾을 수 없습니다.
"""
        raise RuntimeError(error_msg)

    @staticmethod
    def find_zebra_printers() -> List[Dict]:
        """
        Zebra 프린터 검색

        Returns:
            [
                {
                    'vendor_id': int,
                    'product_id': int,
                    'manufacturer': str,
                    'product': str,
                    'serial': str,
                    'bus': int,
                    'address': int
                },
                ...
            ]
        """
        # Backend 가져오기
        backend = PrinterDiscovery._get_libusb_backend()

        printers = []

        # Zebra VID로 검색
        devices = usb.core.find(
            find_all=True,
            idVendor=PrinterDiscovery.ZEBRA_VENDOR_ID,
            backend=backend
        )

        for dev in devices:
            try:
                printer_info = {
                    'vendor_id': dev.idVendor,
                    'product_id': dev.idProduct,
                    'manufacturer': usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else 'Unknown',
                    'product': usb.util.get_string(dev, dev.iProduct) if dev.iProduct else 'Unknown',
                    'serial': usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else '',
                    'bus': dev.bus,
                    'address': dev.address,
                }
                printers.append(printer_info)

            except Exception as e:
                # 접근 권한 문제 등으로 정보를 가져올 수 없는 경우
                printer_info = {
                    'vendor_id': dev.idVendor,
                    'product_id': dev.idProduct,
                    'manufacturer': 'Unknown',
                    'product': 'Unknown',
                    'serial': '',
                    'bus': dev.bus,
                    'address': dev.address,
                    'error': str(e)
                }
                printers.append(printer_info)

        return printers

    @staticmethod
    def find_printer_by_vid_pid(vendor_id: int, product_id: int) -> Optional[Dict]:
        """
        VID/PID로 프린터 검색

        Args:
            vendor_id: Vendor ID
            product_id: Product ID

        Returns:
            프린터 정보 dict 또는 None
        """
        # Backend 가져오기
        backend = PrinterDiscovery._get_libusb_backend()

        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, backend=backend)

        if dev is None:
            return None

        try:
            return {
                'vendor_id': dev.idVendor,
                'product_id': dev.idProduct,
                'manufacturer': usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else 'Unknown',
                'product': usb.util.get_string(dev, dev.iProduct) if dev.iProduct else 'Unknown',
                'serial': usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else '',
                'bus': dev.bus,
                'address': dev.address,
            }
        except Exception as e:
            return {
                'vendor_id': dev.idVendor,
                'product_id': dev.idProduct,
                'manufacturer': 'Unknown',
                'product': 'Unknown',
                'serial': '',
                'bus': dev.bus,
                'address': dev.address,
                'error': str(e)
            }

    @staticmethod
    def find_all_printers() -> List[Dict]:
        """
        모든 USB 프린터 검색 (Class 7: Printer)

        Returns:
            프린터 정보 리스트
        """
        # Backend 가져오기
        backend = PrinterDiscovery._get_libusb_backend()

        printers = []

        # USB Printer Class (0x07)
        devices = usb.core.find(
            find_all=True,
            bDeviceClass=0x07,  # Printer class
            backend=backend
        )

        for dev in devices:
            try:
                printer_info = {
                    'vendor_id': dev.idVendor,
                    'product_id': dev.idProduct,
                    'manufacturer': usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else 'Unknown',
                    'product': usb.util.get_string(dev, dev.iProduct) if dev.iProduct else 'Unknown',
                    'serial': usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else '',
                    'bus': dev.bus,
                    'address': dev.address,
                }
                printers.append(printer_info)

            except Exception:
                continue

        return printers
