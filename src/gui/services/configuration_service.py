"""설정 관리 서비스

애플리케이션 설정 및 데이터 로드를 담당합니다.
"""

from datetime import datetime
from typing import Optional

from ...utils.serial_number_generator import SerialNumberGenerator


class ConfigurationService:
    """설정 관리 서비스"""

    # 설정 키 목록
    SETTING_KEYS = [
        'printer_selection', 'prn_template', 'serial_port',
        'serial_baudrate', 'serial_timeout', 'auto_increment',
        'use_mac_in_label', 'auto_print_on_mac_detected',
        'backup_enabled', 'backup_interval', 'backup_path'
    ]

    def __init__(self, db):
        """
        Args:
            db: DBManager 인스턴스
        """
        self.db = db

    def load_home_data(self, latest_mac_address: Optional[str] = None) -> dict:
        """홈 화면 데이터 로드

        Args:
            latest_mac_address: 감지된 MAC 주소 (선택)

        Returns:
            홈 화면에 필요한 모든 데이터
        """
        # 오늘 통계
        stats = self.db.get_today_stats()

        # LOT 설정
        lot_config = self.db.get_lot_config()

        # 다음 시리얼 번호 계산
        next_serial, next_sequence = self._calculate_next_serial(lot_config)

        # 오늘 출력 리스트
        today = datetime.now().strftime('%Y-%m-%d')
        history = self.db.get_print_history(
            limit=1000,
            date_from=today,
            date_to=today
        )

        # 마지막 출력 시리얼 번호
        last_serial = history[0]['serial_number'] if history else '-'

        return {
            'stats': stats,
            'lot_config': lot_config,
            'next_serial': next_serial,
            'next_sequence': next_sequence,
            'last_serial': last_serial,
            'history': history,
            'mac_address': latest_mac_address
        }

    def _calculate_next_serial(self, lot_config: dict) -> tuple:
        """다음 시리얼 번호 계산

        Returns:
            (next_serial, next_sequence) 튜플
        """
        # 현재 LOT 번호 생성
        current_lot = self._get_lot_number(lot_config)

        # Auto Increment 설정
        auto_increment = self.db.get_config('auto_increment') != 'false'

        # 최대 생산순서 조회
        max_seq = self.db.get_max_sequence_for_lot(current_lot)

        # 다음 생산순서 결정
        if max_seq is None:
            next_sequence = '0001'
        elif auto_increment:
            next_sequence = str(max_seq + 1).zfill(4)
        else:
            next_sequence = str(max_seq).zfill(4)

        # 시리얼 번호 생성
        lot_config_copy = lot_config.copy()
        lot_config_copy['production_sequence'] = next_sequence

        sn_params = {
            k: v for k, v in lot_config_copy.items()
            if k in [
                'model_code', 'dev_code', 'robot_spec', 'suite_spec',
                'hw_code', 'assembly_code', 'reserved',
                'production_date', 'production_sequence'
            ]
        }
        sn_gen = SerialNumberGenerator(**sn_params)
        next_serial = sn_gen.generate()

        return next_serial, next_sequence

    def _get_lot_number(self, lot_config: dict) -> str:
        """LOT 번호 생성"""
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

    def load_lot_config(self) -> dict:
        """LOT 설정 로드"""
        return self.db.get_lot_config()

    def save_lot_config(self, config: dict) -> None:
        """LOT 설정 저장"""
        self.db.update_lot_config(**config)

    def load_settings(self) -> dict:
        """앱 설정 로드"""
        settings = {}
        for key in self.SETTING_KEYS:
            value = self.db.get_config(key)
            if value is not None:
                settings[key] = value
        return settings

    def save_settings(self, settings: dict) -> None:
        """앱 설정 저장"""
        for key, value in settings.items():
            self.db.set_config(key, value)

    def get_config(self, key: str) -> Optional[str]:
        """단일 설정값 조회"""
        return self.db.get_config(key)
