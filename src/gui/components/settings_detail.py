"""설정 상세 패널 (VSCode 스타일)"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QStackedWidget
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from ..core import Theme, LayoutSystem
from .setting_item import (
    SelectSettingItem,
    InputSettingItem,
    CheckboxSettingItem,
    SelectWithButtonSettingItem
)
from ...printer.printer_discovery import PrinterDiscovery
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
        self._create_label_panel()
        self._create_backup_panel()

    def _create_scroll_panel(self, title):
        """스크롤 가능한 패널 생성"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme.colors.GRAY_50};
            }}
        """)

        # 컨텐츠 위젯
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 24, 40, 24)
        content_layout.setSpacing(0)

        # 타이틀
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.H3}px;
            font-weight: {self.theme.fonts.BOLD};
            color: {self.theme.colors.GRAY_900};
            margin-bottom: 24px;
        """)
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

        layout.addStretch()

        self.addWidget(panel)
        self.panels["output.automation"] = self.indexOf(panel)

    def _create_label_panel(self):
        """라벨 설정 패널"""
        panel, layout = self._create_scroll_panel("출력 > 라벨 설정")

        # MAC 주소 사용
        self.use_mac_item = CheckboxSettingItem(
            "use_mac_in_label",
            "Use MAC Address in Label",
            default=True,
            description="바코드 라벨 출력 시 MAC 주소를 포함합니다.",
            theme=self.theme
        )
        self.use_mac_item.value_changed.connect(self._on_checkbox_changed)
        layout.addWidget(self.use_mac_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["output.label"] = self.indexOf(panel)

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

        # 백업 경로 (읽기 전용 표시)
        self.backup_path_item = InputSettingItem(
            "backup_path",
            "Backup Path",
            placeholder="backup/",
            default="backup/",
            description="백업 파일이 저장되는 경로입니다. (읽기 전용)",
            theme=self.theme
        )
        self.backup_path_item.input.setReadOnly(True)
        layout.addWidget(self.backup_path_item)

        layout.addStretch()

        self.addWidget(panel)
        self.panels["system.backup"] = self.indexOf(panel)

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

    def _on_refresh_printers(self):
        """프린터 새로고침"""
        printer_options = self._scan_printers()
        self.printer_item.combo.clear()
        self.printer_item.combo.addItems(printer_options if printer_options else ["연결된 프린터 없음"])
        self.printer_item.combo.setCurrentIndex(0)

    def _scan_printers(self):
        """프린터 검색"""
        try:
            printers = PrinterDiscovery.find_all_printers()
            options = ["자동 검색 (권장)"]

            for printer in printers:
                manufacturer = printer.get('manufacturer', 'Unknown')
                product = printer.get('product', 'Unknown')
                vid = printer.get('vendor_id', 0)
                pid = printer.get('product_id', 0)
                bus = printer.get('bus', '?')
                address = printer.get('address', '?')

                vid_pid = f"VID:0x{vid:04X}, PID:0x{pid:04X}"

                if manufacturer != 'Unknown' and product != 'Unknown':
                    option_text = f"{manufacturer} {product} ({vid_pid}, Bus {bus}, Addr {address})"
                else:
                    option_text = f"USB Printer ({vid_pid}, Bus {bus}, Addr {address})"

                options.append(option_text)

            if len(options) == 1:
                options.append("연결된 프린터 없음")

            return options
        except Exception as e:
            print(f"프린터 검색 오류: {e}")
            return ["자동 검색 (권장)", "연결된 프린터 없음"]

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
