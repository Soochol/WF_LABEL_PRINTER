"""설정 상세 패널 (VSCode 스타일)"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QStackedWidget, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from ..core import Theme, LayoutSystem
from .setting_item import (
    SelectSettingItem,
    InputSettingItem,
    CheckboxSettingItem,
    SelectWithButtonSettingItem,
    InputWithButtonSettingItem
)
from ...printer.zebra_win_controller import ZebraWinController
import serial.tools.list_ports
from pathlib import Path

class SettingsDetailPanel(QStackedWidget):
    """설정 상세 패널 (스택 위젯)"""

    setting_changed = pyqtSignal(str, object)  # (setting_key, value)
    refresh_printers_requested = pyqtSignal()

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 각 카테고리별 패널 생성
        self.panels = {}
        self._create_printer_panel()
        self._create_serial_panel()
        self._create_automation_panel()
        self._create_backup_panel()

    def _create_scroll_panel(self, title):
        """스크롤 가능한 패널 생성"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("DetailScrollArea")  # QSS 셀렉터용

        # 컨텐츠 위젯
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 24, 40, 24)
        content_layout.setSpacing(0)

        # 타이틀
        title_label = QLabel(title)
        title_label.setObjectName("DetailPanelTitle")  # QSS 셀렉터용
        title_label.setProperty("data-role", "panel-title")  # QSS 셀렉터용
        content_layout.addWidget(title_label)

        scroll.setWidget(content)

        return scroll, content_layout

    def _create_printer_panel(self):
        """프린터 설정 패널"""
        panel, layout = self._create_scroll_panel("하드웨어 > 프린터")

        # 프린터 선택
        printer_options = self._scan_printers()
        self.printer_item = SelectWithButtonSettingItem(
            "printer_selection",
            "Printer Selection",
            printer_options if printer_options else ["연결된 프린터 없음"],
            "🔄 새로고침",
            default=printer_options[0] if printer_options else "연결된 프린터 없음",
            description="USB로 연결된 프린터를 선택하세요. 네트워크 프린터는 지원하지 않습니다.",
            theme=self.theme
        )
        self.printer_item.value_changed.connect(self.setting_changed.emit)
        self.printer_item.button_clicked.connect(self._on_refresh_printers)
        layout.addWidget(self.printer_item)

        # PRN 템플릿
        prn_templates = self._scan_prn_templates()
        self.template_item = SelectSettingItem(
            "prn_template",
            "PRN Template",
            prn_templates if prn_templates else ["템플릿 없음"],
            default=prn_templates[0] if prn_templates else "템플릿 없음",
            description="인쇄에 사용할 ZPL 템플릿 파일을 선택하세요.",
            theme=self.theme
        )
        self.template_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.template_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["hardware.printer"] = self.indexOf(panel)

    def _create_serial_panel(self):
        """시리얼 포트 설정 패널"""
        panel, layout = self._create_scroll_panel("하드웨어 > 시리얼 포트")

        # 포트
        com_ports = self._scan_com_ports()
        self.serial_port_item = SelectSettingItem(
            "serial_port",
            "Port",
            com_ports if com_ports else ["포트 없음"],
            default=com_ports[0] if com_ports else "포트 없음",
            description="MCU와 통신할 시리얼 포트를 선택하세요.",
            theme=self.theme
        )
        self.serial_port_item.value_changed.connect(self._on_serial_port_changed)
        layout.addWidget(self.serial_port_item)

        # 보드레이트
        self.serial_baudrate_item = SelectSettingItem(
            "serial_baudrate",
            "Baud Rate",
            ["9600", "19200", "38400", "57600", "115200"],
            default="115200",
            description="시리얼 통신 속도를 선택하세요.",
            theme=self.theme
        )
        self.serial_baudrate_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.serial_baudrate_item)

        # 타임아웃
        self.serial_timeout_item = InputSettingItem(
            "serial_timeout",
            "Timeout (seconds)",
            placeholder="30",
            default="30",
            description="시리얼 통신 타임아웃 시간 (초)을 설정하세요.",
            theme=self.theme
        )
        self.serial_timeout_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.serial_timeout_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["hardware.serial"] = self.indexOf(panel)

    def _create_automation_panel(self):
        """자동화 설정 패널"""
        panel, layout = self._create_scroll_panel("출력 > 자동화")

        # 자동 증가
        self.auto_increment_item = SelectSettingItem(
            "auto_increment",
            "Auto Increment Production Sequence",
            ["사용", "사용 안 함"],
            default="사용",
            description="인쇄 후 생산순서를 자동으로 1 증가시킵니다.",
            theme=self.theme
        )
        self.auto_increment_item.value_changed.connect(self._on_auto_increment_combo_changed)
        layout.addWidget(self.auto_increment_item)

        # MAC 주소 사용
        self.use_mac_item = SelectSettingItem(
            "use_mac_in_label",
            "Use MAC Address in Label",
            ["사용", "사용 안 함"],
            default="사용",
            description="바코드 라벨 출력 시 MAC 주소를 포함합니다.",
            theme=self.theme
        )
        self.use_mac_item.value_changed.connect(self._on_mac_combo_changed)
        layout.addWidget(self.use_mac_item)

        # MAC 감지 시 자동 인쇄
        self.auto_print_on_mac_item = SelectSettingItem(
            "auto_print_on_mac_detected",
            "Auto Print on MAC Detected",
            ["사용", "사용 안 함"],
            default="사용 안 함",
            description="MAC 주소 감지 시 자동으로 라벨을 인쇄합니다.",
            theme=self.theme
        )
        self.auto_print_on_mac_item.value_changed.connect(self._on_auto_print_mac_combo_changed)
        layout.addWidget(self.auto_print_on_mac_item)

        # 인쇄 매수
        self.print_copies_item = SelectSettingItem(
            "print_copies",
            "Print Copies",
            ["1", "2", "3", "4", "5"],
            default="1",
            description="한 번 인쇄 시 출력할 라벨 매수를 설정합니다.",
            theme=self.theme
        )
        self.print_copies_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.print_copies_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["output.automation"] = self.indexOf(panel)


    def _create_backup_panel(self):
        """백업 설정 패널"""
        panel, layout = self._create_scroll_panel("시스템 > 백업")

        # 백업 활성화
        self.backup_enabled_item = SelectSettingItem(
            "backup_enabled",
            "Enable Auto Backup",
            ["사용", "사용 안 함"],
            default="사용",
            description="데이터베이스를 주기적으로 자동 백업합니다.",
            theme=self.theme
        )
        self.backup_enabled_item.value_changed.connect(self._on_backup_enabled_changed)
        layout.addWidget(self.backup_enabled_item)

        # 백업 주기
        self.backup_interval_item = InputSettingItem(
            "backup_interval",
            "Backup Interval (seconds)",
            placeholder="3600",
            default="3600",
            description="백업 주기를 초 단위로 설정하세요. (3600초 = 1시간)",
            theme=self.theme
        )
        self.backup_interval_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.backup_interval_item)

        # 백업 경로 (폴더 선택 버튼 포함)
        self.backup_path_item = InputWithButtonSettingItem(
            "backup_path",
            "Backup Path",
            "폴더 선택",
            placeholder="기본 경로 (비어있으면 AppData 사용)",
            default="",
            description="백업 파일이 저장되는 폴더 경로입니다. 비어있으면 기본 경로를 사용합니다.",
            theme=self.theme
        )
        self.backup_path_item.input.setReadOnly(True)  # 직접 입력 불가, 버튼으로만 선택
        self.backup_path_item.button_clicked.connect(self._on_select_backup_path)
        self.backup_path_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.backup_path_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["system.backup"] = self.indexOf(panel)

    def _on_select_backup_path(self):
        """백업 경로 폴더 선택 대화상자"""
        # 현재 경로 가져오기
        current_path = self.backup_path_item.get_value()
        if not current_path or not Path(current_path).exists():
            current_path = str(Path.home())  # 기본값: 사용자 홈 디렉토리

        # 폴더 선택 대화상자
        folder = QFileDialog.getExistingDirectory(
            self,
            "백업 폴더 선택",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            # 선택한 폴더 경로를 입력 필드에 설정
            self.backup_path_item.set_value(folder)
            # 설정 변경 이벤트 발생
            self.setting_changed.emit("backup_path", folder)

    def _on_backup_enabled_changed(self, key, value):
        """백업 활성화 콤보박스 값 변경 시 - '사용'/'사용 안 함'을 'true'/'false'로 변환"""
        str_value = 'true' if value == '사용' else 'false'
        self.setting_changed.emit(key, str_value)

    def show_category(self, category_id):
        """카테고리 표시"""
        if category_id in self.panels:
            self.setCurrentIndex(self.panels[category_id])

    def _on_serial_port_changed(self, key, value):
        """시리얼 포트 값 변경 시 - COM5 - USB... 형식에서 COM5만 추출"""
        if ' - ' in value:
            port_only = value.split(' - ')[0]
            self.setting_changed.emit(key, port_only)
        else:
            self.setting_changed.emit(key, value)

    def _on_checkbox_changed(self, key, value):
        """체크박스 값 변경 시 - boolean을 'true'/'false' 문자열로 변환"""
        str_value = 'true' if value else 'false'
        self.setting_changed.emit(key, str_value)

    def _on_auto_increment_combo_changed(self, key, value):
        """자동 증가 콤보박스 값 변경 시 - '사용'/'사용 안 함'을 'true'/'false'로 변환"""
        str_value = 'true' if value == '사용' else 'false'
        self.setting_changed.emit(key, str_value)

    def _on_mac_combo_changed(self, key, value):
        """MAC 콤보박스 값 변경 시 - '사용'/'사용 안 함'을 'true'/'false'로 변환"""
        str_value = 'true' if value == '사용' else 'false'
        self.setting_changed.emit(key, str_value)

    def _on_auto_print_mac_combo_changed(self, key, value):
        """MAC 자동 인쇄 콤보박스 값 변경 시 - '사용'/'사용 안 함'을 'true'/'false'로 변환"""
        str_value = 'true' if value == '사용' else 'false'
        self.setting_changed.emit(key, str_value)

    def _on_refresh_printers(self):
        """프린터 새로고침"""
        printer_options = self._scan_printers()
        self.printer_item.combo.clear()
        self.printer_item.combo.addItems(printer_options if printer_options else ["연결된 프린터 없음"])
        self.printer_item.combo.setCurrentIndex(0)

    def _scan_printers(self):
        """프린터 검색 (시스템 프린터 큐)"""
        options = ["자동 검색 (권장)"]

        try:
            zebra_ctrl = ZebraWinController()

            # 시스템 프린터 큐 목록 가져오기
            queues = zebra_ctrl.get_available_printers()

            for queue in queues:
                # Zebra 프린터만 표시
                if 'zebra' in queue.lower() or 'zdesigner' in queue.lower() or 'zpl' in queue.lower():
                    options.append(f"[프린터 큐] {queue}")

            print(f"프린터 큐 검색 완료: {len(queues)}개 발견")

            if len(options) == 1:
                options.append("연결된 프린터 없음 - 프린터 드라이버를 설치하세요")

            return options

        except Exception as e:
            print(f"프린터 검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return ["자동 검색 (권장)", "⚠️ 프린터 검색 오류 - 콘솔 메시지를 확인하세요"]

    def _scan_com_ports(self):
        """COM 포트 검색"""
        try:
            ports = serial.tools.list_ports.comports()
            port_list = []

            for port in sorted(ports, key=lambda p: p.device):
                port_info = f"{port.device} - {port.description}"
                port_list.append(port_info)

            return port_list if port_list else ["포트 없음"]
        except Exception as e:
            print(f"COM 포트 검색 오류: {e}")
            return ["포트 없음"]

    def _scan_prn_templates(self):
        """PRN 템플릿 검색"""
        try:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            prn_folder = project_root / "prn"

            if not prn_folder.exists():
                return []

            prn_files = list(prn_folder.glob("*.prn"))
            return [f.name for f in sorted(prn_files)]
        except Exception as e:
            print(f"PRN 템플릿 검색 오류: {e}")
            return []
