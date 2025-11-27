"""홈 화면 - 카드 기반 대시보드 디자인"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QScrollArea, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import ComponentBase, Theme
from ..components import PrintHistoryTable
from ..styles import get_theme_manager


class Card(QFrame):
    """기본 카드 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # 테마 변경 연결
        theme_mgr = get_theme_manager()
        theme_mgr.theme_changed.connect(self._on_theme_changed)

    def _apply_base_style(self):
        """기본 카드 스타일"""
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors
        return f"""
            background-color: {colors.WHITE};
            border: 1px solid {colors.GRAY_200};
            border-radius: 12px;
        """

    def _on_theme_changed(self, _):
        self._apply_style()

    def _apply_style(self):
        """서브클래스에서 오버라이드"""
        pass


class StatCard(Card):
    """통계 카드"""

    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        # 최소/최대 크기로 유연하게 설정
        self.setMinimumSize(120, 80)
        self.setMaximumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._value_color = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # 타이틀
        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatCardTitle")
        layout.addWidget(self.title_label)

        # 값
        self.value_label = QLabel(value)
        self.value_label.setObjectName("StatCardValue")
        layout.addWidget(self.value_label)

        layout.addStretch()
        self._apply_style()

    def _apply_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.setStyleSheet(f"""
            QFrame#StatCard {{
                {self._apply_base_style()}
            }}
        """)

        self.title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 500;
            color: {colors.GRAY_500};
            background: transparent;
        """)

        value_color = self._value_color if self._value_color else colors.GRAY_900
        self.value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {value_color};
            background: transparent;
        """)

    def set_value(self, value: str, color: str = None):
        self.value_label.setText(value)
        if color:
            self._value_color = color
            self._apply_style()


class InfoCard(Card):
    """정보 표시 카드 (시리얼 정보, MAC 주소 등)"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)
        self.setMaximumHeight(70)
        self._value_color = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # 타이틀
        self.title_label = QLabel(title)
        self.title_label.setObjectName("InfoCardTitle")
        self.title_label.setMinimumWidth(80)
        self.title_label.setMaximumWidth(120)
        layout.addWidget(self.title_label)

        # 값
        self.value_label = QLabel("-")
        self.value_label.setObjectName("InfoCardValue")
        self.value_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self.value_label)

        self._apply_style()

    def _apply_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.setStyleSheet(f"""
            QFrame#InfoCard {{
                {self._apply_base_style()}
            }}
        """)

        self.title_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 500;
            color: {colors.GRAY_500};
            background: transparent;
        """)

        value_color = self._value_color if self._value_color else colors.GRAY_900
        self.value_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {value_color};
            background: transparent;
        """)

    def set_value(self, value: str, color: str = None):
        self.value_label.setText(value)
        self._value_color = color
        self._apply_style()


class ActionCard(Card):
    """액션 버튼 카드"""

    print_clicked = pyqtSignal()
    test_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActionCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(70)
        self.setMaximumHeight(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 테스트 인쇄 버튼
        self.test_btn = QPushButton("테스트 인쇄")
        self.test_btn.setObjectName("SecondaryButton")
        self.test_btn.setMinimumSize(100, 40)
        self.test_btn.setMaximumSize(140, 48)
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.clicked.connect(self.test_clicked.emit)
        layout.addWidget(self.test_btn)

        # 인쇄 시작 버튼
        self.print_btn = QPushButton("인쇄 시작")
        self.print_btn.setObjectName("PrimaryButton")
        self.print_btn.setMinimumSize(100, 40)
        self.print_btn.setMaximumSize(140, 48)
        self.print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.print_btn.clicked.connect(self.print_clicked.emit)
        layout.addWidget(self.print_btn)

        layout.addStretch()
        self._apply_style()

    def _apply_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.setStyleSheet(f"""
            QFrame#ActionCard {{
                {self._apply_base_style()}
            }}
        """)

        self.test_btn.setStyleSheet(f"""
            QPushButton#SecondaryButton {{
                background-color: {colors.GRAY_100};
                color: {colors.GRAY_700};
                border: 1px solid {colors.GRAY_300};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton#SecondaryButton:hover {{
                background-color: {colors.GRAY_200};
                border-color: {colors.GRAY_400};
            }}
            QPushButton#SecondaryButton:pressed {{
                background-color: {colors.GRAY_300};
            }}
        """)

        self.print_btn.setStyleSheet(f"""
            QPushButton#PrimaryButton {{
                background-color: {colors.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {colors.PRIMARY_DARK};
            }}
            QPushButton#PrimaryButton:pressed {{
                background-color: {colors.PRIMARY_DARK};
            }}
        """)

    def set_buttons_enabled(self, enabled: bool):
        self.test_btn.setEnabled(enabled)
        self.print_btn.setEnabled(enabled)


class HistoryCard(Card):
    """출력 기록 카드"""

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("HistoryCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 헤더
        header = QHBoxLayout()
        title = QLabel("출력 기록")
        title.setObjectName("HistoryCardTitle")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # 테이블 (유연한 크기)
        self.table = PrintHistoryTable(self.theme)
        self.table.table.setMinimumHeight(150)
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.table)

        self._apply_style()

    def _apply_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.setStyleSheet(f"""
            QFrame#HistoryCard {{
                {self._apply_base_style()}
            }}
        """)

        for child in self.findChildren(QLabel):
            if child.objectName() == "HistoryCardTitle":
                child.setStyleSheet(f"""
                    font-size: 15px;
                    font-weight: 600;
                    color: {colors.GRAY_900};
                    background: transparent;
                """)

    def set_history(self, history_list):
        self.table.set_history(history_list)


class HomeView(ComponentBase):
    """홈 뷰 - 카드 기반 대시보드"""

    reset_clicked = pyqtSignal()
    print_requested = pyqtSignal()
    test_requested = pyqtSignal()

    def __init__(self, theme=None, parent=None):
        super().__init__()
        self.theme = theme or Theme()
        self.setObjectName("HomeView")

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 스크롤 컨텐츠
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # ========== 헤더 ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title = QLabel("Dashboard")
        title.setProperty("data-role", "view-title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setProperty("data-role", "view-secondary")
        refresh_btn.setMinimumHeight(32)
        refresh_btn.setMaximumHeight(40)
        refresh_btn.setMinimumWidth(80)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self._on_reset)
        header_layout.addWidget(refresh_btn)

        content_layout.addLayout(header_layout)

        # ========== 통계 카드 Row ==========
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.today_card = StatCard("오늘 출력", "0")
        self.success_card = StatCard("성공", "0")
        self.failed_card = StatCard("실패", "0")

        stats_layout.addWidget(self.today_card)
        stats_layout.addWidget(self.success_card)
        stats_layout.addWidget(self.failed_card)
        stats_layout.addStretch()

        content_layout.addLayout(stats_layout)

        # ========== 정보 카드 Row ==========
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        self.last_serial_card = InfoCard("마지막 출력")
        self.next_serial_card = InfoCard("다음 시리얼")
        self.mac_card = InfoCard("감지된 MAC")
        self.mac_card.set_value("대기 중...")

        info_layout.addWidget(self.last_serial_card)
        info_layout.addWidget(self.next_serial_card)
        info_layout.addWidget(self.mac_card)

        content_layout.addLayout(info_layout)

        # ========== 액션 카드 ==========
        self.action_card = ActionCard()
        self.action_card.print_clicked.connect(self._on_print)
        self.action_card.test_clicked.connect(self._on_test)
        content_layout.addWidget(self.action_card)

        # ========== 출력 기록 카드 ==========
        self.history_card = HistoryCard(self.theme)
        content_layout.addWidget(self.history_card, 1)  # stretch factor 1

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 스크롤 영역 스타일
        self._apply_scroll_style()

        # 테마 변경 연결
        theme_mgr = get_theme_manager()
        theme_mgr.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _):
        self._apply_scroll_style()

    def _apply_scroll_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.GRAY_400};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.GRAY_500};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

    def _on_reset(self):
        self.reset_clicked.emit()

    def _on_test(self):
        self.test_requested.emit()

    def _on_print(self):
        self.print_requested.emit()

    def set_stats(self, today_count, success_count, failed_count):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.today_card.set_value(str(today_count))
        self.success_card.set_value(str(success_count), color=colors.SUCCESS)
        self.failed_card.set_value(str(failed_count), color=colors.ERROR)

    def set_serial_info(self, last_serial, next_serial):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        self.last_serial_card.set_value(last_serial or "-")
        self.next_serial_card.set_value(next_serial or "-", color=colors.PRIMARY)

    def set_mac_address(self, mac_address):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        if mac_address:
            self.mac_card.set_value(mac_address, color=colors.SUCCESS)
        else:
            self.mac_card.set_value("대기 중...", color=colors.GRAY_500)

    def set_history(self, history_list):
        self.history_card.set_history(history_list)

    def set_print_buttons_enabled(self, enabled: bool):
        self.action_card.set_buttons_enabled(enabled)
