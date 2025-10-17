"""LOT 설정 트리 네비게이션 (VSCode 스타일)"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import Theme

class LotConfigTree(QTreeWidget):
    """LOT 설정 트리 네비게이션"""

    category_selected = pyqtSignal(str, str)  # (category_id, category_name)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 트리 설정
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(False)

        # VSCode 스타일 적용
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {self.theme.colors.GRAY_50};
                border: none;
                outline: none;
                font-size: {self.theme.fonts.BODY}px;
                color: {self.theme.colors.GRAY_700};
            }}
            QTreeWidget::item {{
                padding: 8px 12px;
                border: none;
            }}
            QTreeWidget::item:hover {{
                background-color: {self.theme.colors.GRAY_100};
            }}
            QTreeWidget::item:selected {{
                background-color: {self.theme.colors.GRAY_200};
                color: {self.theme.colors.PRIMARY};
            }}
            QTreeWidget::branch {{
                background-color: {self.theme.colors.GRAY_50};
            }}
            QTreeWidget::branch:hover {{
                background-color: {self.theme.colors.GRAY_100};
            }}
        """)

        # 트리 구조 생성
        self._build_tree()

        # 시그널 연결
        self.itemClicked.connect(self._on_item_clicked)

        # 초기 선택
        first_item = self.topLevelItem(0)
        if first_item and first_item.childCount() > 0:
            first_child = first_item.child(0)
            self.setCurrentItem(first_child)
            self._on_item_clicked(first_child, 0)

    def _build_tree(self):
        """트리 구조 생성"""
        # LOT 설정
        lot_root = QTreeWidgetItem(self, ["LOT 설정"])
        lot_root.setExpanded(True)

        # 기본 정보
        basic = QTreeWidgetItem(lot_root, ["기본 정보"])
        basic.setData(0, Qt.ItemDataRole.UserRole, "basic")

        # 사양 정보
        spec = QTreeWidgetItem(lot_root, ["사양 정보"])
        spec.setData(0, Qt.ItemDataRole.UserRole, "spec")

    def _on_item_clicked(self, item, column):
        """트리 항목 클릭"""
        category_id = item.data(0, Qt.ItemDataRole.UserRole)

        if category_id:
            category_name = item.text(0)
            self.category_selected.emit(category_id, category_name)
