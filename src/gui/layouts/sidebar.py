"""사이드바 레이아웃"""
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from ..core import ComponentBase, LayoutSystem
from ..styles import get_theme_manager
from ..utils import SvgIcon

class Sidebar(ComponentBase):
    """사이드바"""
    page_changed = pyqtSignal(str)  # "home", "print", "config", "settings", "history"
    theme_toggle_requested = pyqtSignal()  # 다크 모드 토글 요청

    def __init__(self, theme=None, parent=None):
        super().__init__(parent, fixed_width=LayoutSystem.SIDEBAR_WIDTH)
        self.current_page = "home"
        self.setObjectName("Sidebar")  # QSS 셀렉터용

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # 앱 타이틀
        title = QLabel("WF LABEL\nPRINTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(100)
        title.setProperty("data-role", "app-title")  # QSS 셀렉터용
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

        # 다크 모드 토글 버튼
        self.theme_toggle_btn = QPushButton("🌙 다크 모드")
        self.theme_toggle_btn.setProperty("data-role", "theme-toggle")  # QSS 셀렉터용
        self.theme_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_toggle_btn.clicked.connect(self._on_theme_toggle)
        layout.addWidget(self.theme_toggle_btn)

        layout.addSpacing(16)

        # 초기 선택
        self._set_active("home")

    def _create_menu_button(self, text, page_id):
        """메뉴 버튼 생성 (SVG 아이콘 포함)"""
        btn = QPushButton(text)
        btn.setFixedHeight(LayoutSystem.ROW_HEIGHT)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("page_id", page_id)
        btn.clicked.connect(lambda: self._on_menu_clicked(page_id))

        # SVG 아이콘 설정 (테마에 맞는 색상)
        theme_mgr = get_theme_manager()
        icon = SvgIcon.create_icon(page_id, theme_mgr.colors.GRAY_600, 20)
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))

        # 스타일은 QSS에서 처리 (_sidebar.qss)
        return btn

    def _on_theme_toggle(self):
        """테마 토글 버튼 클릭"""
        self.theme_toggle_requested.emit()

    def set_theme_mode(self, is_dark: bool):
        """테마 모드에 따라 버튼 텍스트 및 아이콘 업데이트

        Args:
            is_dark: True면 다크 모드
        """
        if is_dark:
            self.theme_toggle_btn.setText("☀️ 라이트 모드")
        else:
            self.theme_toggle_btn.setText("🌙 다크 모드")

        # 아이콘 색상 업데이트
        self._set_active(self.current_page)

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

        # 테마에서 색상 가져오기
        theme_mgr = get_theme_manager()
        inactive_color = theme_mgr.colors.GRAY_600  # 비활성: 테마에 맞는 회색

        # 모든 버튼 비활성화 및 아이콘 색상 업데이트
        for btn_id, btn in btn_map.items():
            btn.setProperty("active", "false")
            # 비활성 상태 아이콘 (테마에 맞는 색상)
            icon = SvgIcon.create_icon(btn_id, inactive_color, 20)
            btn.setIcon(icon)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # 선택된 버튼 활성화 및 아이콘 색상 업데이트
        if page_id in btn_map:
            btn_map[page_id].setProperty("active", "true")
            # 활성 상태 아이콘 (프라이머리 색상)
            active_icon = SvgIcon.create_icon(
                page_id, theme_mgr.colors.PRIMARY, 20
            )
            btn_map[page_id].setIcon(active_icon)
            btn_map[page_id].style().unpolish(btn_map[page_id])
            btn_map[page_id].style().polish(btn_map[page_id])

    def set_current_page(self, page_id):
        """외부에서 페이지 설정"""
        self._set_active(page_id)
