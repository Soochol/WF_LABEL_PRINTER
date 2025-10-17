"""설정 화면 (VSCode 스타일)"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from ..core import ComponentBase, Theme
from ..components import SettingsTree, SettingsDetailPanel

class SettingsView(ComponentBase):
    """설정 뷰 (VSCode 스타일 좌우 분할)"""

    settings_saved = pyqtSignal(dict)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 즉시 저장용 타이머 (디바운싱)
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._save_all_settings)

        # 메인 레이아웃
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 좌우 분할 스플리터
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {self.theme.colors.GRAY_300};
            }}
        """)

        # 좌측: 트리 네비게이션 (30%)
        self.tree = SettingsTree(self.theme)
        self.tree.category_selected.connect(self._on_category_selected)

        # 우측: 설정 상세 패널 (70%)
        self.detail_panel = SettingsDetailPanel(self.theme)
        self.detail_panel.setting_changed.connect(self._on_setting_changed)

        # 스플리터에 추가
        splitter.addWidget(self.tree)
        splitter.addWidget(self.detail_panel)

        # 초기 비율 설정 (30:70)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

    def _on_category_selected(self, category_id, category_name):
        """카테고리 선택 시"""
        self.detail_panel.show_category(category_id)

    def _on_setting_changed(self, setting_key, value):
        """설정 값 변경 시 - 즉시 저장 (디바운싱)"""
        print(f"설정 변경: {setting_key} = {value}")

        # 타이머 재시작 (500ms 후 저장)
        self.save_timer.stop()
        self.save_timer.start(500)

    def _save_all_settings(self):
        """모든 설정 저장"""
        settings = self.get_settings()
        print(f"설정 저장 중...")
        self.settings_saved.emit(settings)

    def get_settings(self):
        """현재 설정값 가져오기"""
        return {
            'printer_selection': self.detail_panel.printer_item.get_value(),
            'prn_template': self.detail_panel.template_item.get_value(),
            'serial_port': self._extract_com_port(self.detail_panel.serial_port_item.get_value()),
            'serial_baudrate': self.detail_panel.serial_baudrate_item.get_value(),
            'serial_timeout': self.detail_panel.serial_timeout_item.get_value(),
            'auto_increment': 'true' if self.detail_panel.auto_increment_item.get_value() == '사용' else 'false',
            'use_mac_in_label': 'true' if self.detail_panel.use_mac_item.get_value() == '사용' else 'false',
            'backup_enabled': 'true' if self.detail_panel.backup_enabled_item.get_value() == '사용' else 'false',
            'backup_interval': self.detail_panel.backup_interval_item.get_value()
        }

    def set_settings(self, settings):
        """설정값 적용"""
        # 프린터
        if 'printer_selection' in settings:
            self.detail_panel.printer_item.set_value(settings['printer_selection'])

        # PRN 템플릿
        if 'prn_template' in settings:
            self.detail_panel.template_item.set_value(settings['prn_template'])

        # 시리얼 포트 (COM5 -> COM5 - ... 형식으로 매칭)
        if 'serial_port' in settings:
            saved_port = settings['serial_port']
            combo = self.detail_panel.serial_port_item.combo
            found = False
            for i in range(combo.count()):
                item_text = combo.itemText(i)
                if item_text.startswith(saved_port + ' - ') or item_text == saved_port:
                    combo.setCurrentIndex(i)
                    found = True
                    break
            if not found and combo.count() > 0:
                combo.setCurrentIndex(0)

        # 보드레이트
        if 'serial_baudrate' in settings:
            self.detail_panel.serial_baudrate_item.set_value(settings['serial_baudrate'])

        # 타임아웃
        if 'serial_timeout' in settings:
            self.detail_panel.serial_timeout_item.set_value(settings['serial_timeout'])

        # 자동 증가
        if 'auto_increment' in settings:
            value = '사용' if settings['auto_increment'] == 'true' else '사용 안 함'
            self.detail_panel.auto_increment_item.set_value(value)

        # MAC 주소 사용
        if 'use_mac_in_label' in settings:
            value = '사용' if settings['use_mac_in_label'] == 'true' else '사용 안 함'
            self.detail_panel.use_mac_item.set_value(value)

        # 백업
        if 'backup_enabled' in settings:
            value = '사용' if settings['backup_enabled'] == 'true' else '사용 안 함'
            self.detail_panel.backup_enabled_item.set_value(value)

        if 'backup_interval' in settings:
            self.detail_panel.backup_interval_item.set_value(settings['backup_interval'])

    def _extract_com_port(self, port_value):
        """COM 포트 추출 (COM5 - USB... -> COM5)"""
        if ' - ' in port_value:
            return port_value.split(' - ')[0]
        return port_value
