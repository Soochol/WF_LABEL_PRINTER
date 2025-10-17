"""메인 레이아웃"""
from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget
from ..core import ComponentBase, LayoutSystem, Theme
from .sidebar import Sidebar
from ..views.home_view import HomeView
from ..views.lot_config_view import LotConfigView
from ..views.settings_view import SettingsView
from ..views.history_view import HistoryView

class MainLayout(ComponentBase):
    """메인 레이아웃 - 사이드바 + 페이지"""

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # 사이드바
        self.sidebar = Sidebar(self.theme)
        self.sidebar.page_changed.connect(self._on_page_changed)

        # 뷰 스택
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {self.theme.colors.GRAY_50};")

        # 뷰 생성
        self.home_view = HomeView(self.theme)
        self.config_view = LotConfigView(self.theme)
        self.settings_view = SettingsView(self.theme)
        self.history_view = HistoryView(self.theme)

        # 스택에 추가
        self.stack.addWidget(self.home_view)      # index 0
        self.stack.addWidget(self.config_view)    # index 1
        self.stack.addWidget(self.settings_view)  # index 2
        self.stack.addWidget(self.history_view)   # index 3

        # 페이지 매핑
        self.page_map = {
            "home": 0,
            "config": 1,
            "settings": 2,
            "history": 3
        }

        # 레이아웃 조립
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, stretch=1)

        # 초기 페이지
        self._on_page_changed("home")

    def _on_page_changed(self, page_id):
        """페이지 변경"""
        if page_id in self.page_map:
            self.stack.setCurrentIndex(self.page_map[page_id])

    def show_page(self, page_id):
        """외부에서 페이지 변경"""
        self.sidebar.set_current_page(page_id)
        self._on_page_changed(page_id)

    def get_view(self, page_id):
        """뷰 가져오기"""
        views = {
            "home": self.home_view,
            "config": self.config_view,
            "settings": self.settings_view,
            "history": self.history_view
        }
        return views.get(page_id)
