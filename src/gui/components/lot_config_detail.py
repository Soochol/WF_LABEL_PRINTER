"""LOT 설정 상세 패널 (VSCode 스타일)"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QStackedWidget
from PyQt6.QtCore import pyqtSignal
from ..core import Theme, LayoutSystem
from .setting_item import SelectSettingItem

class LotConfigDetailPanel(QStackedWidget):
    """LOT 설정 상세 패널"""

    setting_changed = pyqtSignal(str, object)  # (setting_key, value)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 각 카테고리별 패널 생성
        self.panels = {}
        self._create_basic_panel()
        self._create_spec_panel()

    def _create_scroll_panel(self, title):
        """스크롤 가능한 패널 생성"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme.colors.GRAY_50};
            }}
        """)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 24, 40, 24)
        content_layout.setSpacing(0)

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

    def _create_basic_panel(self):
        """기본 정보 패널"""
        panel, layout = self._create_scroll_panel("LOT 설정 > 기본 정보")

        # 모델명 코드
        self.model_code_item = SelectSettingItem(
            "model_code",
            "Model Code",
            ["P10", "W10", "M10", "A10"],
            default="P10",
            description="제품 모델명 코드를 선택하세요.",
            theme=self.theme
        )
        self.model_code_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.model_code_item)

        # 개발 코드
        dev_code_options = {
            'P': 'P (Pilot)',
            'M': 'M (Manufacturing/양산)',
            'T': 'T (Test)',
            'D': 'D (Demo/시연품)',
            'R': 'R (Replacement/교체품)'
        }
        self.dev_code_item = SelectSettingItem(
            "dev_code",
            "Development Code",
            dev_code_options,
            default="D",
            description="개발 단계 코드를 선택하세요.",
            theme=self.theme
        )
        self.dev_code_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.dev_code_item)

        layout.addStretch()
        self.addWidget(panel)
        self.panels["basic"] = self.indexOf(panel)

    def _create_spec_panel(self):
        """사양 정보 패널"""
        panel, layout = self._create_scroll_panel("LOT 설정 > 사양 정보")

        # 로봇 사양
        robot_spec_options = {
            'L0': 'L0 (L230-A39)',
            'L1': 'L1 (L210-A39)',
            'L2': 'L2 (L220-A39)',
            'L3': 'L3 (L220-A43)',
            'L4': 'L4 (L220-A47)',
            'L5': 'L5 (L200-39)',
            'L6': 'L6 (L200-43)',
            'L7': 'L7 (L200-47)',
            'L8': 'L8'
        }
        self.robot_spec_item = SelectSettingItem(
            "robot_spec",
            "Robot Specification",
            robot_spec_options,
            default="L0",
            description="로봇 사양 코드를 선택하세요.",
            theme=self.theme
        )
        self.robot_spec_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.robot_spec_item)

        # Suite 사양
        self.suite_spec_item = SelectSettingItem(
            "suite_spec",
            "Suite Specification",
            ["S0", "S1", "S2"],
            default="S0",
            description="Suite 사양 코드를 선택하세요.",
            theme=self.theme
        )
        self.suite_spec_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.suite_spec_item)

        # HW 코드
        self.hw_code_item = SelectSettingItem(
            "hw_code",
            "Hardware Code",
            ["H1", "H2", "H3", "H4"],
            default="H3",
            description="하드웨어 버전 코드를 선택하세요.",
            theme=self.theme
        )
        self.hw_code_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.hw_code_item)

        # 조립 코드
        self.assembly_code_item = SelectSettingItem(
            "assembly_code",
            "Assembly Code",
            ["A0", "A1"],
            default="A0",
            description="조립 방식 코드를 선택하세요.",
            theme=self.theme
        )
        self.assembly_code_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.assembly_code_item)

        # 예약 코드
        self.reserved_item = SelectSettingItem(
            "reserved",
            "Reserved Code",
            ["0", "1", "2", "3"],
            default="0",
            description="예약 코드를 선택하세요.",
            theme=self.theme
        )
        self.reserved_item.value_changed.connect(self.setting_changed.emit)
        layout.addWidget(self.reserved_item)

        layout.addStretch()
        self.addWidget(panel)
        self.panels["spec"] = self.indexOf(panel)


    def show_category(self, category_id):
        """카테고리 표시"""
        if category_id in self.panels:
            self.setCurrentIndex(self.panels[category_id])

    def get_config(self):
        """현재 설정값 가져오기"""
        return {
            'model_code': self.model_code_item.get_value(),
            'dev_code': self.dev_code_item.get_value(),
            'robot_spec': self.robot_spec_item.get_value(),
            'suite_spec': self.suite_spec_item.get_value(),
            'hw_code': self.hw_code_item.get_value(),
            'assembly_code': self.assembly_code_item.get_value(),
            'reserved': self.reserved_item.get_value()
        }

    def set_config(self, config):
        """설정값 적용"""
        if 'model_code' in config:
            self.model_code_item.set_value(config['model_code'])
        if 'dev_code' in config:
            self.dev_code_item.set_value(config['dev_code'])
        if 'robot_spec' in config:
            self.robot_spec_item.set_value(config['robot_spec'])
        if 'suite_spec' in config:
            self.suite_spec_item.set_value(config['suite_spec'])
        if 'hw_code' in config:
            self.hw_code_item.set_value(config['hw_code'])
        if 'assembly_code' in config:
            self.assembly_code_item.set_value(config['assembly_code'])
        if 'reserved' in config:
            self.reserved_item.set_value(config['reserved'])
