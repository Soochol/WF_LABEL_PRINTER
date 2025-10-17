"""LOT 설정 화면 (VSCode 스타일)"""
from PyQt6.QtWidgets import QHBoxLayout, QSplitter
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from ..core import ComponentBase, Theme
from ..components.lot_config_tree import LotConfigTree
from ..components.lot_config_detail import LotConfigDetailPanel

class LotConfigView(ComponentBase):
    """LOT 설정 뷰 (VSCode 스타일 좌우 분할)"""

    config_saved = pyqtSignal(dict)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 즉시 저장용 타이머 (디바운싱)
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._save_all_config)

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
        self.tree = LotConfigTree(self.theme)
        self.tree.category_selected.connect(self._on_category_selected)

        # 우측: 설정 상세 패널 (70%)
        self.detail_panel = LotConfigDetailPanel(self.theme)
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
        print(f"LOT 설정 변경: {setting_key} = {value}")

        # 타이머 재시작 (500ms 후 저장)
        self.save_timer.stop()
        self.save_timer.start(500)

    def _save_all_config(self):
        """모든 설정 저장"""
        config = self.get_config()
        print(f"LOT 설정 저장 중...")
        self.config_saved.emit(config)

    def get_config(self):
        """현재 설정값 가져오기"""
        return self.detail_panel.get_config()

    def set_config(self, config):
        """설정값 적용"""
        self.detail_panel.set_config(config)

    def hideEvent(self, event):
        """페이지를 벗어날 때 즉시 저장"""
        super().hideEvent(event)
        # 디바운싱 타이머가 실행 중이면 즉시 저장
        if self.save_timer.isActive():
            self.save_timer.stop()
            self._save_all_config()
            print("LOT 설정 페이지 벗어남 - 즉시 저장 완료")
