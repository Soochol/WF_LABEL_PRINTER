"""인쇄 처리 서비스

인쇄 관련 비즈니스 로직을 담당합니다.
- 생산순서 계산
- 인쇄 실행
- 인쇄 결과 저장
"""

from datetime import datetime
from typing import Optional


class PrintService:
    """인쇄 처리 서비스"""

    def __init__(self, db, print_controller):
        """
        Args:
            db: DBManager 인스턴스
            print_controller: PrintController 인스턴스
        """
        self.db = db
        self.print_controller = print_controller

    def get_lot_number(self, lot_config: dict) -> str:
        """LOT 번호 생성 (날짜 제외한 모든 필드 조합)

        LOT 번호 = model + dev + robot_spec + suite_spec + hw + assembly + reserved + production_date
        """
        return (
            lot_config.get('model_code', '') +
            lot_config.get('dev_code', '') +
            lot_config.get('robot_spec', '') +
            lot_config.get('suite_spec', '') +
            lot_config.get('hw_code', '') +
            lot_config.get('assembly_code', '') +
            lot_config.get('reserved', '') +
            lot_config.get('production_date', '')
        )

    def calculate_next_sequence(self, lot_config: dict) -> str:
        """다음 생산순서 계산

        Args:
            lot_config: LOT 설정 딕셔너리

        Returns:
            다음 생산순서 (4자리 문자열, 예: "0001")
        """
        current_lot = self.get_lot_number(lot_config)
        max_seq = self.db.get_max_sequence_for_lot(current_lot)
        auto_increment = self.db.get_config('auto_increment') != 'false'

        if max_seq is None:
            return '0001'

        if auto_increment:
            return str(max_seq + 1).zfill(4)
        return str(max_seq).zfill(4)

    def execute_print(
        self,
        lot_config: dict,
        mac_address: Optional[str],
        test_mode: bool = False
    ) -> dict:
        """인쇄 실행

        Args:
            lot_config: LOT 설정 (production_sequence 포함)
            mac_address: MAC 주소 (None이면 테스트 모드에서 "TEST-MAC" 사용)
            test_mode: 테스트 모드 여부

        Returns:
            인쇄 결과 딕셔너리 {'success': bool, 'message': str, ...}

        Raises:
            ValueError: MAC 주소나 템플릿이 없는 경우
        """
        # 설정 로드
        printer_selection = self.db.get_config('printer_selection') or '자동 검색 (권장)'
        prn_template = self.db.get_config('prn_template')
        use_mac_in_label = self.db.get_config('use_mac_in_label') != 'false'
        print_copies = int(self.db.get_config('print_copies') or '1')

        if not prn_template:
            raise ValueError("PRN 템플릿이 설정되지 않았습니다. 설정 화면에서 템플릿을 선택하세요.")

        # MAC 주소 처리
        if use_mac_in_label:
            if not test_mode and not mac_address:
                raise ValueError(
                    "MAC 주소가 감지되지 않았습니다. "
                    "ESP32 전원을 확인하거나 '라벨 설정'에서 MAC 사용을 비활성화하세요."
                )
            mac_to_use = mac_address if mac_address else "TEST-MAC"
        else:
            mac_to_use = "NONE"

        # 인쇄 실행
        return self.print_controller.print_label(
            lot_config=lot_config,
            mac_address=mac_to_use,
            template_name=prn_template,
            printer_selection=printer_selection,
            test_mode=test_mode,
            use_mac_in_label=use_mac_in_label,
            print_copies=print_copies
        )

    def save_print_result(
        self,
        result: dict,
        lot_config: dict,
        prn_template: str
    ) -> None:
        """인쇄 결과 저장 (실제 인쇄만)

        Args:
            result: 인쇄 결과 딕셔너리
            lot_config: LOT 설정 (production_sequence 포함)
            prn_template: 사용된 PRN 템플릿 이름
        """
        print_date = datetime.now().strftime('%Y-%m-%d')

        self.db.save_print_history(
            serial_number=result['serial_number'],
            mac_address=result['mac_address'],
            print_date=print_date,
            status='success',
            error_message=None,
            prn_template=prn_template
        )

        # 생산순서 업데이트
        self.db.update_lot_config(
            production_sequence=lot_config['production_sequence']
        )
