"""사이드바 레이아웃"""
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from ..core import ComponentBase, LayoutSystem, Theme
from ..utils import SvgIcon

class Sidebar(ComponentBase):
    """사이드바"""
    page_changed = pyqtSignal(str)  # "home", "print", "config", "settings", "history"

    def __init__(self, theme=None, parent=None):
        super().__init__(parent, fixed_width=LayoutSystem.SIDEBAR_WIDTH)
        self.theme = theme or Theme()
        self.current_page = "home"

        self.setStyleSheet(f"""
            background-color: {self.theme.colors.GRAY_900};
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # 앱 타이틀
        title = QLabel("WF LABEL\nPRINTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(100)
        title.setStyleSheet(f"""
            font-size: {self.theme.fonts.H2}px;
            font-weight: {self.theme.fonts.BOLD};
            color: {self.theme.colors.WHITE};
            background-color: {self.theme.colors.PRIMARY};
            padding: 20px 0;
        """)
        layout.addWidget(title)

        # 메뉴 버튼들
        layout.addSpacing(20)

        self.home_btn = self._create_menu_button("홈", "home")
        self.config_btn = self._create_menu_button("LOT 설정", "config")
        self.settings_btn = self._create_menu_button("설정", "settings")
        self.history_btn = self._create_menu_button("이력", "history")

        layout.addWidget(self.home_btn)
        layout.addWidget(self.config_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.history_btn)

        layout.addStretch()

        # 초기 선택
        self._set_active("home")

    def _create_menu_button(self, text, page_id):
        """메뉴 버튼 생성 (SVG 아이콘 포함)"""
        btn = QPushButton(text)
        btn.setFixedHeight(LayoutSystem.ROW_HEIGHT)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("page_id", page_id)
        btn.clicked.connect(lambda: self._on_menu_clicked(page_id))

        # SVG 아이콘 설정
        icon = SvgIcon.create_icon(page_id, "#000000", 20)
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))

        # 기본 스타일
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: 48px;
                font-size: {self.theme.fonts.BODY}px;
                font-weight: {self.theme.fonts.MEDIUM};
                color: #000000;
                background-color: transparent;
                border: none;
                border-left: 4px solid transparent;
                outline: none;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
            QPushButton[active="true"] {{
                background-color: {self.theme.colors.GRAY_800};
                color: {self.theme.colors.PRIMARY};
                border-left: 4px solid {self.theme.colors.PRIMARY};
            }}
        """)

        return btn

    def _on_menu_clicked(self, page_id):
        """메뉴 클릭"""
        self._set_active(page_id)
        self.page_changed.emit(page_id)

    def _set_active(self, page_id):
        """활성 페이지 설정"""
        self.current_page = page_id

        # 버튼 맵핑
        btn_map = {
            "home": self.home_btn,
            "config": self.config_btn,
            "settings": self.settings_btn,
            "history": self.history_btn
        }

        # 모든 버튼 비활성화 및 아이콘 색상 업데이트
        for btn_id, btn in btn_map.items():
            btn.setProperty("active", "false")
            # 비활성 상태 아이콘 (검은색)
            icon = SvgIcon.create_icon(btn_id, "#000000", 20)
            btn.setIcon(icon)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # 선택된 버튼 활성화 및 아이콘 색상 업데이트
        if page_id in btn_map:
            btn_map[page_id].setProperty("active", "true")
            # 활성 상태 아이콘 (프라이머리 색상)
            active_icon = SvgIcon.create_icon(
                page_id, self.theme.colors.PRIMARY, 20
            )
            btn_map[page_id].setIcon(active_icon)
            btn_map[page_id].style().unpolish(btn_map[page_id])
            btn_map[page_id].style().polish(btn_map[page_id])

    def set_current_page(self, page_id):
        """외부에서 페이지 설정"""
        self._set_active(page_id)
