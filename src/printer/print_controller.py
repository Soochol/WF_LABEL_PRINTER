"""인쇄 컨트롤러 - 인쇄 프로세스 오케스트레이션"""
from pathlib import Path
from datetime import datetime
from ..utils.serial_number_generator import SerialNumberGenerator
from .zebra_win_controller import ZebraWinController
from .prn_parser import PRNParser

class PrintController:
    """인쇄 컨트롤러"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

    def _get_test_zpl_data(self) -> str:
        """테스트 인쇄용 - PRN 템플릿의 모든 설정을 따르되 간단한 TEST LABEL 문구만 출력"""
        return """CT~~CD,~CC^~CT~
^XA
~TA000
~JSN
^LT0
^MNW
^MTT
^PON
^PMN
^LH0,0
^JMA
^PR1,1
~SD28
^JUS
^LRN
^CI27
^PA0,1,1,0
^XZ
^XA
^MMT
^PW480
^LL240
^LS0
^FT100,100^A0N,40,40^FDTEST LABEL^FS
^PQ1,,,Y
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
        """PRN 템플릿 로드 및 변수 치환 (PRNParser 사용)"""
        if not template_path.exists():
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

        # PRNParser를 사용하여 변수 치환 및 ZPL 처리
        parser = PRNParser(str(template_path))

        # 날짜 생성
        date_str = datetime.now().strftime('%Y.%m.%d')

        # MAC 주소 처리
        mac_for_label = mac_address if use_mac_in_label else ''

        # PRNParser의 replace_variables 메서드 사용
        # 이 메서드는 변수 치환 + ^FH\ regex 처리를 모두 수행
        zpl_data = parser.replace_variables(date_str, serial_number, mac_for_label)

        # 디버깅: QR 코드 데이터 확인 및 ZPL 저장
        lines = zpl_data.split('\n')
        for i, line in enumerate(lines):
            if '^BQ' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                print(f"[DEBUG] QR Code at line {i+1}:")
                print(f"  Command: {line}")
                print(f"  Data:    {next_line}")

        # ZPL 데이터를 파일로 저장 (디버깅용)
        debug_zpl_path = self.project_root / "debug_last_print.zpl"
        with open(debug_zpl_path, 'w', encoding='utf-8') as f:
            f.write(zpl_data)
        print(f"[DEBUG] ZPL saved to: {debug_zpl_path}")

        return zpl_data

    def _send_to_printer(self, zpl_data: str, printer_selection: str):
        """프린터로 ZPL 데이터 전송 (시스템 프린터 큐 사용)"""
        try:
            # ZebraWinController 사용
            zebra_ctrl = ZebraWinController()

            # 프린터 선택
            if printer_selection == "자동 검색 (권장)":
                # 첫 번째 Zebra 프린터 자동 선택
                zebra_printers = zebra_ctrl.get_zebra_printers()
                if not zebra_printers:
                    raise RuntimeError("시스템에 설치된 Zebra 프린터를 찾을 수 없습니다. 프린터 드라이버를 설치하세요.")

                queue_name = zebra_printers[0]
                print(f"자동 선택된 프린터: {queue_name}")
            else:
                # 설정에서 선택한 프린터 사용
                # "[프린터 큐] ZDesigner ZT231-203dpi ZPL" 형식으로 저장되어 있을 수 있음
                if printer_selection.startswith("[프린터 큐] "):
                    queue_name = printer_selection.replace("[프린터 큐] ", "")
                else:
                    # 이전 형식 또는 직접 입력된 큐 이름
                    queue_name = printer_selection
                print(f"선택된 프린터: {queue_name}")

            # 프린터 연결
            zebra_ctrl.connect(queue_name)

            # ZPL 전송
            zebra_ctrl.send_zpl(zpl_data)

            print(f"✓ 프린터로 ZPL 전송 완료 (큐: {queue_name})")

        except Exception as e:
            raise RuntimeError(f"프린터 전송 실패: {e}")
