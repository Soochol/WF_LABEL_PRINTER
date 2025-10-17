"""인쇄 컨트롤러 - 인쇄 프로세스 오케스트레이션"""
from pathlib import Path
from datetime import datetime
import usb.core
from ..utils.serial_number_generator import SerialNumberGenerator
from .printer_discovery import PrinterDiscovery

class PrintController:
    """인쇄 컨트롤러"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

    def _get_test_zpl_data(self) -> str:
        """테스트 인쇄용 - ZEBRA TEST LABEL 문구 출력 (480x240 dots 라벨 크기)"""
        return """^XA
^PW480
^LL240
^FO100,100^A0N,40,40^FDZEBRA TEST LABEL^FS
^XZ"""

    def print_label(
        self,
        lot_config: dict,
        mac_address: str,
        template_name: str,
        printer_selection: str = "자동 검색 (권장)",
        test_mode: bool = False,
        use_mac_in_label: bool = True
    ) -> dict:
        """
        라벨 인쇄

        Args:
            lot_config: LOT 설정 (model_code, dev_code, ...)
            mac_address: MAC 주소
            template_name: PRN 템플릿 파일명
            printer_selection: 프린터 선택 정보
            test_mode: 테스트 모드 (True면 간단한 TEST 라벨 출력)
            use_mac_in_label: MAC 주소 사용 여부 (False면 MAC 치환 안 함)

        Returns:
            {
                'success': bool,
                'serial_number': str,
                'mac_address': str,
                'message': str
            }
        """
        try:
            if test_mode:
                # 테스트 모드: 간단한 "ZEBRA TEST LABEL" 문구만 출력
                zpl_data = self._get_test_zpl_data()
                self._send_to_printer(zpl_data, printer_selection)

                return {
                    'success': True,
                    'serial_number': 'TEST-LABEL',
                    'mac_address': 'TEST-MODE',
                    'message': '테스트 인쇄 성공'
                }
            else:
                # 실제 인쇄: 기존 로직
                # 1. 시리얼 번호 생성
                serial_number = self._generate_serial_number(lot_config)

                # 2. PRN 템플릿 로드
                template_path = self.project_root / "prn" / template_name
                zpl_data = self._load_and_replace_template(
                    template_path,
                    serial_number,
                    mac_address,
                    use_mac_in_label
                )

                # 3. 프린터로 전송
                self._send_to_printer(zpl_data, printer_selection)

                return {
                    'success': True,
                    'serial_number': serial_number,
                    'mac_address': mac_address,
                    'message': '인쇄 성공'
                }

        except Exception as e:
            return {
                'success': False,
                'serial_number': '',
                'mac_address': mac_address if not test_mode else 'TEST-MODE',
                'message': f'인쇄 실패: {str(e)}'
            }

    def _generate_serial_number(self, lot_config: dict) -> str:
        """시리얼 번호 생성"""
        sn_params = {k: v for k, v in lot_config.items() if k in [
            'model_code', 'dev_code', 'robot_spec', 'suite_spec',
            'hw_code', 'assembly_code', 'reserved', 'production_date', 'production_sequence'
        ]}
        sn_gen = SerialNumberGenerator(**sn_params)
        return sn_gen.generate()

    def _load_and_replace_template(
        self,
        template_path: Path,
        serial_number: str,
        mac_address: str,
        use_mac_in_label: bool = True
    ) -> str:
        """PRN 템플릿 로드 및 변수 치환"""
        if not template_path.exists():
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

        # 템플릿 로드
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # 변수 치환
        date_str = datetime.now().strftime('%Y-%m-%d')

        # 공통 변수 치환
        zpl_data = template.replace('VAR_SERIALNUMBER', serial_number)
        zpl_data = zpl_data.replace('VAR_DATE', date_str)

        # MAC 주소 사용하는 경우만 치환
        if use_mac_in_label:
            zpl_data = zpl_data.replace('VAR_MAC', mac_address)
            zpl_data = zpl_data.replace('VAR_2DBARCODE', f'{serial_number}|{mac_address}')

        return zpl_data

    def _send_to_printer(self, zpl_data: str, printer_selection: str):
        """프린터로 ZPL 데이터 전송"""
        # 프린터 선택
        if printer_selection == "자동 검색 (권장)":
            # 첫 번째 프린터 사용
            printers = PrinterDiscovery.find_all_printers()
            if not printers:
                raise RuntimeError("사용 가능한 프린터가 없습니다")
            printer_info = printers[0]
        else:
            # 특정 프린터 선택 (VID/PID 파싱)
            # 예: "Zebra ZD420 (VID:0x0A5F, PID:0x0084, ...)"
            printer_info = self._parse_printer_selection(printer_selection)

        # USB 장치 찾기
        backend = PrinterDiscovery._get_libusb_backend()
        device = usb.core.find(
            idVendor=printer_info['vendor_id'],
            idProduct=printer_info['product_id'],
            backend=backend
        )

        if device is None:
            raise RuntimeError(f"프린터를 찾을 수 없습니다: VID=0x{printer_info['vendor_id']:04X}, PID=0x{printer_info['product_id']:04X}")

        # 장치 설정
        try:
            if device.is_kernel_driver_active(0):
                device.detach_kernel_driver(0)
        except:
            pass

        device.set_configuration()

        # Endpoint 찾기 (OUT endpoint)
        cfg = device.get_active_configuration()
        intf = cfg[(0, 0)]

        ep_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )

        if ep_out is None:
            raise RuntimeError("프린터 Endpoint를 찾을 수 없습니다")

        # ZPL 데이터 전송
        zpl_bytes = zpl_data.encode('utf-8')
        ep_out.write(zpl_bytes)

        print(f"✓ 프린터로 {len(zpl_bytes)} 바이트 전송 완료")

    def _parse_printer_selection(self, selection: str) -> dict:
        """프린터 선택 문자열 파싱"""
        # "Zebra ZD420 (VID:0x0A5F, PID:0x0084, Bus 1, Addr 5)"
        # 또는 "USB Printer (VID:0x1234, PID:0x5678, ...)"

        import re
        vid_match = re.search(r'VID:0x([0-9A-Fa-f]+)', selection)
        pid_match = re.search(r'PID:0x([0-9A-Fa-f]+)', selection)

        if not vid_match or not pid_match:
            raise ValueError(f"프린터 정보를 파싱할 수 없습니다: {selection}")

        return {
            'vendor_id': int(vid_match.group(1), 16),
            'product_id': int(pid_match.group(1), 16)
        }
