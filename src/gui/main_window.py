from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
from .core import Theme
from .layouts.main_layout import MainLayout
from .components import ToastManager, StatusBar
from ..database.db_manager import DBManager
from ..utils.serial_number_generator import SerialNumberGenerator
from ..printer.print_controller import PrintController
from ..printer.zebra_win_controller import ZebraWinController
from ..mcu.mcu_monitor import MCUMonitor

class MainWindow(QMainWindow):
    """메인 윈도우

    체크리스트 준수:
    - ✅ 중앙 위젯 설정 (setCentralWidget)
    - ✅ 초기화 순서 준수
    - ✅ 윈도우 크기 설정
    - ✅ 시그널/슬롯 연결
    - ✅ DB 연결 및 데이터 로드
    """

    def __init__(self, debug_mode=False):
        # ========== 1. 부모 클래스 초기화 ==========
        super().__init__()

        # ========== 2. 윈도우 속성 설정 ==========
        self.setWindowTitle("Zebra Label Printer")
        self.setMinimumSize(800, 600)  # 최소 크기 설정
        self.showMaximized()  # 최대 화면으로 실행

        # ========== 3. 테마 ==========
        self.theme = Theme()
        # 메인 윈도우 배경색 설정 (GRAY_50)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme.colors.GRAY_50};
            }}
            {self.theme.get_global_stylesheet()}
        """)

        # ========== 4. 데이터베이스 초기화 ==========
        self.db = DBManager("data/label_printer.db")
        self.db.initialize()

        # ========== 4-1. 인쇄 컨트롤러 초기화 ==========
        self.print_controller = PrintController()
        self.mcu_monitor = None  # MCU 백그라운드 모니터
        self.latest_mac_address = None  # 감지된 최신 MAC 주소

        # ========== 4-2. 백업 타이머 초기화 ==========
        self.backup_timer = QTimer(self)
        self.backup_timer.timeout.connect(self._do_backup)

        # ========== 5. 중앙 위젯 (메인 레이아웃 + 상태바) ==========
        # 컨테이너 위젯 생성
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 메인 레이아웃 추가
        self.main_layout = MainLayout(self.theme)
        container_layout.addWidget(self.main_layout)

        # 상태바 추가
        self.status_bar = StatusBar(self.theme)
        container_layout.addWidget(self.status_bar)

        # 컨테이너를 중앙 위젯으로 설정
        self.setCentralWidget(container)

        # ========== 5-1. 토스트 관리자 ==========
        self.toast = ToastManager(self, self.theme)

        # ========== 6. 시그널 연결 ==========
        self._connect_signals()

        # ========== 7. 초기 데이터 로드 ==========
        QTimer.singleShot(100, self.load_home_data)
        QTimer.singleShot(150, self.load_settings)
        QTimer.singleShot(200, self._on_history_refresh)
        QTimer.singleShot(300, self._check_printer_status)
        QTimer.singleShot(400, self._start_mcu_monitor)
        QTimer.singleShot(500, self._start_backup_timer)

        # ========== 8. 디버그 모드 (개발용) ==========
        if debug_mode or Theme.DEBUG:
            self._enable_debug_mode()

    def _connect_signals(self):
        """시그널 연결"""
        # Home View
        home_view = self.main_layout.get_view("home")
        if home_view:
            home_view.reset_clicked.connect(self.load_home_data)
            home_view.print_requested.connect(self._on_print_requested)
            home_view.test_requested.connect(self._on_test_requested)

        # Config View
        config_view = self.main_layout.get_view("config")
        if config_view:
            config_view.config_saved.connect(self._on_config_saved)

        # Settings View
        settings_view = self.main_layout.get_view("settings")
        if settings_view:
            settings_view.settings_saved.connect(self._on_settings_saved)

        # History View
        history_view = self.main_layout.get_view("history")
        if history_view:
            history_view.search_requested.connect(self._on_history_search)
            history_view.refresh_requested.connect(self._on_history_refresh)

    def load_home_data(self):
        """홈 화면 데이터 로드"""
        try:
            from datetime import datetime

            # 오늘 통계 조회
            stats = self.db.get_today_stats()

            # LOT 정보 조회
            lot_config = self.db.get_lot_config()

            # 현재 LOT 번호 생성 (생산순서 제외)
            current_lot = self._get_lot_number(lot_config)

            # Auto Increment 설정 확인
            auto_increment = self.db.get_config('auto_increment') != 'false'  # 기본값 true

            # DB에서 해당 LOT의 최대 생산순서 조회
            max_seq = self.db.get_max_sequence_for_lot(current_lot)

            # 다음 생산순서 결정 (인쇄 로직과 동일)
            if max_seq is None:
                # 해당 LOT의 첫 인쇄 → 0001
                next_sequence = '0001'
            else:
                # 기존 LOT 있음
                if auto_increment:
                    # Auto Increment 사용: 최대값 +1
                    next_sequence = str(max_seq + 1).zfill(4)
                else:
                    # Auto Increment 사용 안 함: 동일한 번호 유지
                    next_sequence = str(max_seq).zfill(4)

            # 생산순서를 업데이트하여 다음 시리얼 생성
            lot_config['production_sequence'] = next_sequence

            # 시리얼 번호 생성기로 다음 시리얼 생성
            sn_params = {k: v for k, v in lot_config.items() if k in [
                'model_code', 'dev_code', 'robot_spec', 'suite_spec',
                'hw_code', 'assembly_code', 'reserved', 'production_date', 'production_sequence'
            ]}
            sn_gen = SerialNumberGenerator(**sn_params)
            next_serial = sn_gen.generate()
            lot_code = sn_gen.get_lot_code()
            model = lot_config.get('model_code', '-')

            # 오늘 출력 리스트 조회
            today = datetime.now().strftime('%Y-%m-%d')
            history = self.db.get_print_history(
                limit=1000,  # 충분히 큰 값
                date_from=today,
                date_to=today
            )

            # 마지막 출력 시리얼 번호 (가장 최근 것)
            last_serial = history[0]['serial_number'] if history else '-'

            # HomeView 업데이트
            home_view = self.main_layout.get_view("home")
            if home_view:
                home_view.set_stats(stats['total'], stats['success'], stats['failed'])
                home_view.set_serial_info(last_serial, next_serial)
                home_view.set_mac_address(self.latest_mac_address)
                home_view.set_history(history)

        except Exception as e:
            print(f"홈 데이터 로드 오류: {e}")

    def _on_print_requested(self):
        """인쇄 요청 (실제 인쇄)"""
        self._do_print(test_mode=False)

    def _on_test_requested(self):
        """테스트 인쇄 요청"""
        self._do_print(test_mode=True)

    def _get_lot_number(self, lot_config):
        """LOT 번호 생성 (날짜 제외한 모든 필드 조합)

        LOT 번호 = model + dev + robot_spec + suite_spec + hw + assembly + reserved + production_date
        예: P10DL0S0H3A0C10
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

    def _do_print(self, test_mode: bool = False):
        """실제 인쇄 처리

        Args:
            test_mode: True면 테스트 모드 (DB 저장 안 함)
        """
        home_view = self.main_layout.get_view("home")

        def log(msg):
            """로그 출력 (콘솔만)"""
            print(msg)

        try:
            # 0. 프린터 상태 체크
            self._check_printer_status()

            # 1. LOT 설정 가져오기
            log("LOT 설정 로드 중...")
            lot_config = self.db.get_lot_config()

            # 1-1. LOT 변경 체크 및 생산순서 결정 (실제 인쇄만, 아직 DB에 저장 안 함)
            if not test_mode:
                current_lot = self._get_lot_number(lot_config)
                log(f"현재 LOT: {current_lot}")

                # Auto Increment 설정 확인
                auto_increment = self.db.get_config('auto_increment') != 'false'  # 기본값 true

                # DB에서 현재 LOT의 최대 생산순서 조회
                max_seq = self.db.get_max_sequence_for_lot(current_lot)

                if max_seq is None:
                    # 해당 LOT의 첫 인쇄 → 0001
                    log("✓ 이 LOT의 첫 인쇄: 생산순서 0001")
                    lot_config['production_sequence'] = '0001'
                else:
                    # 해당 LOT 이미 있음
                    if auto_increment:
                        # Auto Increment 사용: 최대값 +1
                        next_seq = str(max_seq + 1).zfill(4)
                        log(f"✓ 동일 LOT 발견 (Auto Increment ON): 생산순서 {str(max_seq).zfill(4)} → {next_seq}")
                        lot_config['production_sequence'] = next_seq
                    else:
                        # Auto Increment 사용 안 함: 동일한 번호 유지
                        same_seq = str(max_seq).zfill(4)
                        log(f"✓ 동일 LOT 발견 (Auto Increment OFF): 생산순서 {same_seq} 유지")
                        lot_config['production_sequence'] = same_seq

                # 주의: 생산순서는 인쇄 성공 후에만 DB에 저장됨

            # 2. 앱 설정 가져오기
            log("앱 설정 로드 중...")
            printer_selection = self.db.get_config('printer_selection') or '자동 검색 (권장)'
            prn_template = self.db.get_config('prn_template')
            use_mac_in_label = self.db.get_config('use_mac_in_label') != 'false'  # 기본값 true

            if not prn_template:
                raise ValueError("PRN 템플릿이 설정되지 않았습니다. 설정 화면에서 템플릿을 선택하세요.")

            # 3. MAC 주소 확인 (라벨에 MAC 사용하는 경우만)
            if use_mac_in_label:
                # 테스트 인쇄는 MAC 없이도 진행 가능
                if not test_mode and not self.latest_mac_address:
                    raise ValueError("MAC 주소가 감지되지 않았습니다. ESP32 전원을 확인하거나 '라벨 설정'에서 MAC 사용을 비활성화하세요.")

                mac_address = self.latest_mac_address if self.latest_mac_address else "TEST-MAC"
                if test_mode and not self.latest_mac_address:
                    log(f"✓ MAC 주소 (테스트 모드): {mac_address}")
                else:
                    log(f"✓ MAC 주소: {mac_address}")
            else:
                # MAC 사용 안 함 - 더미 값 사용
                mac_address = "NONE"
                log("✓ MAC 주소 사용 안 함 (설정에서 비활성화됨)")

            # 4. 인쇄 실행
            mode_text = "테스트 인쇄" if test_mode else "인쇄"
            log(f"{mode_text} 시작...")

            result = self.print_controller.print_label(
                lot_config=lot_config,
                mac_address=mac_address,
                template_name=prn_template,
                printer_selection=printer_selection,
                test_mode=test_mode,
                use_mac_in_label=use_mac_in_label
            )

            # 5. 결과 처리
            if result['success']:
                log(f"✓ {result['message']}")
                log(f"  시리얼 번호: {result['serial_number']}")
                log(f"  MAC 주소: {result['mac_address']}")

                # 6. DB 저장 (실제 인쇄만)
                if not test_mode:
                    log("DB에 저장 중...")

                    # 인쇄 날짜
                    from datetime import datetime
                    print_date = datetime.now().strftime('%Y-%m-%d')

                    # PRN 템플릿
                    prn_template = prn_template

                    self.db.save_print_history(
                        serial_number=result['serial_number'],
                        mac_address=result['mac_address'],
                        print_date=print_date,
                        status='success',
                        error_message=None,
                        prn_template=prn_template
                    )
                    log("✓ DB 저장 완료")

                    # 6-1. 생산순서를 DB에 저장 (인쇄 성공 후에만!)
                    self.db.update_lot_config(production_sequence=lot_config['production_sequence'])
                    log(f"✓ 생산순서 업데이트: {lot_config['production_sequence']}")

                    # 6-2. MAC 주소 초기화 (인쇄 성공 후 다음 인쇄를 위해)
                    self.latest_mac_address = None
                    log("✓ MAC 주소 초기화 완료 (다음 인쇄 대기)")

                    # 7. 홈 화면 새로고침
                    self.load_home_data()

                log(f"\n✓✓✓ {mode_text} 완료! ✓✓✓\n")

                # 성공 토스트 표시
                self.toast.show_success(
                    f"{mode_text} 완료! {result['serial_number']}"
                )
            else:
                log(f"✗ {result['message']}")
                # 실패 토스트 표시
                self.toast.show_error(result['message'])

        except Exception as e:
            mode_text = "테스트 인쇄" if test_mode else "인쇄"
            error_msg = f"{mode_text} 실패: {str(e)}"
            log(f"✗ {error_msg}")

            # 사용자에게 에러 토스트 표시
            self.toast.show_error(error_msg, duration=5000)

    def _on_config_saved(self, config):
        """LOT 설정 저장"""
        print("LOT 설정 저장:", config)
        try:
            self.db.update_lot_config(**config)
            # 홈 화면 새로고침
            self.load_home_data()
        except Exception as e:
            print(f"LOT 설정 저장 오류: {e}")

    def _on_settings_saved(self, settings):
        """앱 설정 저장"""
        print("앱 설정 저장:", settings)
        try:
            # 각 설정값을 DB에 저장
            for key, value in settings.items():
                self.db.set_config(key, value)
            print("✓ 설정이 저장되었습니다")
        except Exception as e:
            print(f"설정 저장 오류: {e}")

    def load_settings(self):
        """설정 화면 데이터 로드"""
        try:
            settings_view = self.main_layout.get_view("settings")
            if not settings_view:
                return

            # DB에서 설정값 로드
            settings = {}
            setting_keys = [
                'printer_selection', 'prn_template', 'serial_port',
                'serial_baudrate', 'serial_timeout', 'auto_increment',
                'use_mac_in_label', 'backup_enabled', 'backup_interval'
            ]

            for key in setting_keys:
                value = self.db.get_config(key)
                if value is not None:
                    settings[key] = value

            # 설정값이 있으면 적용
            if settings:
                settings_view.set_settings(settings)

        except Exception as e:
            print(f"설정 로드 오류: {e}")

    def _on_history_search(self, filters):
        """이력 검색 요청

        Args:
            filters: 검색 필터 딕셔너리
                {
                    'date_from': str,
                    'date_to': str,
                    'serial_number': str or None,
                    'mac_address': str or None
                }
        """
        try:
            history_view = self.main_layout.get_view("history")
            if not history_view:
                return

            # DB 조회
            history = self.db.get_print_history(
                limit=1000,  # 충분히 큰 값
                date_from=filters.get('date_from'),
                date_to=filters.get('date_to'),
                serial_number=filters.get('serial_number'),
                mac_address=filters.get('mac_address')
            )

            # 결과 표시
            history_view.set_history(history, update_count=True)

        except Exception as e:
            print(f"이력 검색 오류: {e}")
            self.toast.show_error(f"검색 실패: {str(e)}")

    def _on_history_refresh(self):
        """이력 새로고침 (전체 기록 표시)"""
        try:
            history_view = self.main_layout.get_view("history")
            if not history_view:
                return

            # 전체 이력 조회
            history = self.db.get_print_history(limit=1000)

            # 결과 표시
            history_view.set_history(history, update_count=True)

        except Exception as e:
            print(f"이력 새로고침 오류: {e}")
            self.toast.show_error(f"새로고침 실패: {str(e)}")

    def _check_printer_status(self):
        """프린터 연결 상태 체크"""
        try:
            zebra_ctrl = ZebraWinController()
            printers = zebra_ctrl.get_zebra_printers()

            if printers:
                # 첫 번째 프린터 정보 표시
                printer_name = printers[0]
                self.status_bar.set_printer_status("connected", printer_name)
            else:
                self.status_bar.set_printer_status("disconnected")
        except Exception as e:
            print(f"프린터 상태 체크 오류: {e}")
            self.status_bar.set_printer_status("disconnected")

    def _start_mcu_monitor(self):
        """MCU 백그라운드 모니터 시작"""
        try:
            # 설정에서 시리얼 포트 정보 가져오기
            serial_port = self.db.get_config('serial_port')
            if not serial_port:
                print("시리얼 포트가 설정되지 않았습니다")
                self.status_bar.set_mcu_status("disconnected")
                return

            serial_baudrate = int(self.db.get_config('serial_baudrate') or '115200')

            # MCU 모니터 생성
            self.mcu_monitor = MCUMonitor(serial_port, serial_baudrate)

            # 시그널 연결
            self.mcu_monitor.connection_status_changed.connect(self._on_mcu_status_changed)
            self.mcu_monitor.mac_detected.connect(self._on_mac_detected)

            # 스레드 시작
            self.mcu_monitor.start()
            print(f"MCU 모니터 시작: {serial_port}")

        except Exception as e:
            print(f"MCU 모니터 시작 오류: {e}")
            self.status_bar.set_mcu_status("disconnected")

    def _on_mcu_status_changed(self, status: str, detail: str):
        """MCU 연결 상태 변경"""
        self.status_bar.set_mcu_status(status, detail)

    def _on_mac_detected(self, mac_address: str):
        """MAC 주소 감지"""
        self.latest_mac_address = mac_address
        print(f"✓ MAC 주소 감지: {mac_address}")

        # 홈 화면 업데이트 (MAC 주소 표시)
        home_view = self.main_layout.get_view("home")
        if home_view:
            home_view.set_mac_address(mac_address)

    def _start_backup_timer(self):
        """백업 타이머 시작"""
        try:
            backup_enabled = self.db.get_config('backup_enabled')
            if backup_enabled == 'true':
                backup_interval = int(self.db.get_config('backup_interval') or '3600')
                self.backup_timer.start(backup_interval * 1000)  # 초 -> 밀리초
                print(f"✓ 자동 백업 활성화: {backup_interval}초 간격")
            else:
                print("자동 백업 비활성화됨")
        except Exception as e:
            print(f"백업 타이머 시작 오류: {e}")

    def _do_backup(self):
        """자동 백업 실행"""
        try:
            from datetime import datetime
            from pathlib import Path

            # 백업 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"label_printer_{timestamp}.db"
            backup_path = f"backup/{backup_filename}"

            # 백업 실행
            self.db.backup(backup_path)
            print(f"✓ 자동 백업 완료: {backup_path}")

        except Exception as e:
            print(f"✗ 자동 백업 실패: {e}")

    def closeEvent(self, event):
        """윈도우 종료 시 리소스 정리"""
        # MCU 모니터 정리
        if self.mcu_monitor:
            self.mcu_monitor.stop()

        # 백업 타이머 정리
        if self.backup_timer:
            self.backup_timer.stop()

        event.accept()

    def _enable_debug_mode(self):
        """디버그 모드 활성화 (개발용)"""
        try:
            from .utils import enable_debug_mode
            enable_debug_mode(self, print_tree=True, show_borders=False)
        except ImportError:
            print("⚠️  디버그 유틸리티를 불러올 수 없습니다.")
