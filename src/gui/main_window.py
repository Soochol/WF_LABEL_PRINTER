"""메인 윈도우 모듈

애플리케이션의 메인 윈도우를 정의합니다.
비즈니스 로직은 services/ 모듈로 분리되어 있습니다.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer

from .core import Theme
from .styles import ThemeManager
from .layouts.main_layout import MainLayout
from .components import ToastManager, StatusBar
from .services import PrintService, ConfigurationService, HistoryService
from ..database.db_manager import DBManager
from ..printer.print_controller import PrintController
from ..printer.zebra_win_controller import ZebraWinController
from ..mcu.mcu_monitor import MCUMonitor


class MainWindow(QMainWindow):
    """메인 윈도우

    역할:
    - UI 레이아웃 구성
    - 시그널/슬롯 연결
    - 서비스 레이어 호출

    비즈니스 로직은 다음 서비스들이 담당:
    - PrintService: 인쇄 처리
    - ConfigurationService: 설정 관리
    - HistoryService: 이력 관리
    """

    def __init__(self, debug_mode=False):
        super().__init__()

        # 윈도우 설정
        self._setup_window()

        # 테마 초기화
        self._setup_theme()

        # 데이터베이스 및 서비스 초기화
        self._setup_database()
        self._setup_services()

        # 장치 초기화
        self._setup_devices()

        # UI 구성
        self._setup_ui()

        # 시그널 연결
        self._connect_signals()

        # 초기 데이터 로드
        self._schedule_initial_load()

        # 디버그 모드
        if debug_mode or Theme.DEBUG:
            self._enable_debug_mode()

    # ==================== 초기화 메서드 ====================

    def _setup_window(self):
        """윈도우 속성 설정"""
        self.setWindowTitle("Zebra Label Printer")
        self.setMinimumSize(800, 600)
        self.showMaximized()

    def _setup_theme(self):
        """테마 초기화"""
        self.theme_manager = ThemeManager()
        self.theme = Theme()  # 하위 호환성
        self.theme_manager.apply_to_app()

        # 개발 모드에서 Hot Reload 활성화
        if not getattr(sys, 'frozen', False):
            self.theme_manager.enable_hot_reload(True)

    def _setup_database(self):
        """데이터베이스 초기화"""
        if getattr(sys, 'frozen', False):
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            self.app_base_dir = Path(base) / "WF_Label_Printer"
        else:
            self.app_base_dir = Path(__file__).parent.parent.parent

        db_path = self.app_base_dir / "data" / "label_printer.db"
        self.db = DBManager(str(db_path))
        self.db.initialize()

    def _setup_services(self):
        """서비스 레이어 초기화"""
        self.print_controller = PrintController()
        self.print_service = PrintService(self.db, self.print_controller)
        self.config_service = ConfigurationService(self.db)
        self.history_service = HistoryService(self.db)

    def _setup_devices(self):
        """장치 관련 초기화"""
        self.mcu_monitor = None
        self.latest_mac_address = None

        # 백업 타이머
        self.backup_timer = QTimer(self)
        self.backup_timer.timeout.connect(self._do_backup)

    def _setup_ui(self):
        """UI 구성"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 메인 레이아웃 (사이드바 + 뷰 스택)
        self.main_layout = MainLayout(self.theme)
        layout.addWidget(self.main_layout)

        # 상태바
        self.status_bar = StatusBar(self.theme)
        layout.addWidget(self.status_bar)

        self.setCentralWidget(container)

        # 토스트 관리자
        self.toast = ToastManager(self, self.theme)

    def _connect_signals(self):
        """시그널 연결"""
        # Home View
        home = self.main_layout.get_view("home")
        if home:
            home.reset_clicked.connect(self._load_home_data)
            home.print_requested.connect(self._on_print)
            home.test_requested.connect(self._on_test_print)

        # Config View
        config = self.main_layout.get_view("config")
        if config:
            config.config_saved.connect(self._on_config_saved)

        # Settings View
        settings = self.main_layout.get_view("settings")
        if settings:
            settings.settings_saved.connect(self._on_settings_saved)

        # History View
        history = self.main_layout.get_view("history")
        if history:
            history.search_requested.connect(self._on_history_search)
            history.refresh_requested.connect(self._on_history_refresh)
            history.delete_requested.connect(self._on_history_delete)

        # Sidebar - 테마 토글
        self.main_layout.sidebar.theme_toggle_requested.connect(
            self._on_theme_toggle
        )

        # ThemeManager - 테마 변경 시그널
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _schedule_initial_load(self):
        """초기 데이터 로드 스케줄링"""
        QTimer.singleShot(100, self._load_home_data)
        QTimer.singleShot(150, self._load_lot_config)
        QTimer.singleShot(200, self._load_settings)
        QTimer.singleShot(250, self._on_history_refresh)
        QTimer.singleShot(350, self._check_printer_status)
        QTimer.singleShot(450, self._start_mcu_monitor)
        QTimer.singleShot(550, self._start_backup_timer)

    # ==================== 홈 화면 ====================

    def _load_home_data(self):
        """홈 화면 데이터 로드"""
        try:
            data = self.config_service.load_home_data(self.latest_mac_address)

            home = self.main_layout.get_view("home")
            if home:
                stats = data['stats']
                home.set_stats(stats['total'], stats['success'], stats['failed'])
                home.set_serial_info(data['last_serial'], data['next_serial'])
                home.set_mac_address(data['mac_address'])
                home.set_history(data['history'])

        except Exception as e:
            print(f"홈 데이터 로드 오류: {e}")

    # ==================== 인쇄 처리 ====================

    def _on_print(self):
        """실제 인쇄 요청"""
        self._execute_print(test_mode=False)

    def _on_test_print(self):
        """테스트 인쇄 요청"""
        self._execute_print(test_mode=True)

    def _execute_print(self, test_mode: bool = False):
        """인쇄 실행

        Args:
            test_mode: 테스트 모드 여부
        """
        home = self.main_layout.get_view("home")
        mode_text = "테스트 인쇄" if test_mode else "인쇄"

        # 버튼 비활성화
        if home:
            home.set_print_buttons_enabled(False)

        try:
            # 프린터 상태 체크
            self._check_printer_status()

            # LOT 설정 로드
            lot_config = self.config_service.load_lot_config()

            # 생산순서 계산 (실제 인쇄만)
            if not test_mode:
                sequence = self.print_service.calculate_next_sequence(lot_config)
                lot_config['production_sequence'] = sequence

            # 인쇄 실행
            result = self.print_service.execute_print(
                lot_config=lot_config,
                mac_address=self.latest_mac_address,
                test_mode=test_mode
            )

            # 결과 처리
            if result['success']:
                # DB 저장 (실제 인쇄만)
                if not test_mode:
                    prn_template = self.config_service.get_config('prn_template')
                    self.print_service.save_print_result(
                        result, lot_config, prn_template
                    )
                    # MAC 주소 초기화
                    self.latest_mac_address = None
                    # 홈 화면 새로고침
                    self._load_home_data()

                self.toast.show_success(
                    f"{mode_text} 완료! {result['serial_number']}"
                )
            else:
                self.toast.show_error(result['message'])

        except Exception as e:
            self.toast.show_error(f"{mode_text} 실패: {str(e)}", duration=5000)

        finally:
            # 버튼 다시 활성화
            if home:
                home.set_print_buttons_enabled(True)

    # ==================== 설정 관리 ====================

    def _load_lot_config(self):
        """LOT 설정 로드"""
        try:
            config_view = self.main_layout.get_view("config")
            if config_view:
                lot_config = self.config_service.load_lot_config()
                if lot_config:
                    config_view.set_config(lot_config)
        except Exception as e:
            print(f"LOT 설정 로드 오류: {e}")

    def _on_config_saved(self, config: dict):
        """LOT 설정 저장"""
        try:
            self.config_service.save_lot_config(config)
            self._load_home_data()
            self.toast.show_success("LOT 설정이 저장되었습니다.")
        except Exception as e:
            self.toast.show_error(f"LOT 설정 저장 실패: {str(e)}")

    def _load_settings(self):
        """앱 설정 로드"""
        try:
            settings_view = self.main_layout.get_view("settings")
            if settings_view:
                settings = self.config_service.load_settings()
                if settings:
                    settings_view.set_settings(settings)
        except Exception as e:
            print(f"설정 로드 오류: {e}")

    def _on_settings_saved(self, settings: dict):
        """앱 설정 저장"""
        try:
            self.config_service.save_settings(settings)
            self.toast.show_success("설정이 저장되었습니다.")
        except Exception as e:
            self.toast.show_error(f"설정 저장 실패: {str(e)}")

    # ==================== 이력 관리 ====================

    def _on_history_search(self, filters: dict):
        """이력 검색"""
        try:
            history_view = self.main_layout.get_view("history")
            if history_view:
                history = self.history_service.search(filters)
                history_view.set_history(history, update_count=True)
        except Exception as e:
            self.toast.show_error(f"검색 실패: {str(e)}")

    def _on_history_refresh(self):
        """이력 새로고침"""
        try:
            history_view = self.main_layout.get_view("history")
            if history_view:
                history = self.history_service.get_all()
                history_view.set_history(history, update_count=True)
        except Exception as e:
            self.toast.show_error(f"새로고침 실패: {str(e)}")

    def _on_history_delete(self, record_id: int):
        """이력 삭제"""
        try:
            if self.history_service.delete(record_id):
                self.toast.show_success("이력이 삭제되었습니다.")
                self._on_history_refresh()
                self._load_home_data()
            else:
                self.toast.show_error("삭제할 항목을 찾을 수 없습니다.")
        except Exception as e:
            self.toast.show_error(f"삭제 실패: {str(e)}")

    # ==================== 장치 관리 ====================

    def _check_printer_status(self):
        """프린터 상태 체크"""
        try:
            zebra = ZebraWinController()
            printers = zebra.get_zebra_printers()
            if printers:
                self.status_bar.set_printer_status("connected", printers[0])
            else:
                self.status_bar.set_printer_status("disconnected")
        except Exception as e:
            print(f"프린터 상태 체크 오류: {e}")
            self.status_bar.set_printer_status("disconnected")

    def _start_mcu_monitor(self):
        """MCU 모니터 시작"""
        try:
            serial_port = self.config_service.get_config('serial_port')
            if not serial_port:
                self.status_bar.set_mcu_status("disconnected")
                return

            baudrate = self.config_service.get_config('serial_baudrate')
            baudrate = int(baudrate) if baudrate else 115200

            self.mcu_monitor = MCUMonitor(serial_port, baudrate)
            self.mcu_monitor.connection_status_changed.connect(
                self._on_mcu_status_changed
            )
            self.mcu_monitor.mac_detected.connect(self._on_mac_detected)
            self.mcu_monitor.start()

        except Exception as e:
            print(f"MCU 모니터 시작 오류: {e}")
            self.status_bar.set_mcu_status("disconnected")

    def _on_mcu_status_changed(self, status: str, detail: str):
        """MCU 상태 변경"""
        self.status_bar.set_mcu_status(status, detail)

    def _on_mac_detected(self, mac_address: str):
        """MAC 주소 감지"""
        self.latest_mac_address = mac_address

        home = self.main_layout.get_view("home")
        if home:
            home.set_mac_address(mac_address)

        # 자동 인쇄 확인
        auto_print = self.config_service.get_config('auto_print_on_mac_detected')
        if auto_print == 'true':
            QTimer.singleShot(100, self._on_print)

    # ==================== 백업 ====================

    def _start_backup_timer(self):
        """백업 타이머 시작"""
        try:
            if self.config_service.get_config('backup_enabled') == 'true':
                interval = self.config_service.get_config('backup_interval')
                interval = int(interval) if interval else 3600
                self.backup_timer.start(interval * 1000)
        except Exception as e:
            print(f"백업 타이머 시작 오류: {e}")

    def _do_backup(self):
        """백업 실행"""
        try:
            from datetime import datetime

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"label_printer_{timestamp}.db"

            user_path = self.config_service.get_config('backup_path')
            if user_path and user_path.strip():
                backup_dir = Path(user_path)
            else:
                backup_dir = self.app_base_dir / "backup"

            self.db.backup(str(backup_dir / filename))

        except Exception as e:
            print(f"백업 실패: {e}")

    # ==================== 테마 ====================

    def _on_theme_toggle(self):
        """테마 토글"""
        self.theme_manager.toggle_theme()

    def _on_theme_changed(self, theme_mode: str):
        """테마 변경 처리"""
        is_dark = theme_mode == "dark"
        self.main_layout.sidebar.set_theme_mode(is_dark)

        mode_text = "다크 모드" if is_dark else "라이트 모드"
        self.toast.show_info(f"{mode_text}로 변경되었습니다")

    # ==================== 리소스 정리 ====================

    def closeEvent(self, event):
        """윈도우 종료 시 리소스 정리"""
        if self.mcu_monitor:
            self.mcu_monitor.stop()

        if self.backup_timer:
            self.backup_timer.stop()

        event.accept()

    def _enable_debug_mode(self):
        """디버그 모드 활성화"""
        try:
            from .utils import enable_debug_mode
            enable_debug_mode(self, print_tree=True, show_borders=False)
        except ImportError:
            pass
