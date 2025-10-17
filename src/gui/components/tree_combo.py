"""Tree + ComboBox 컴포넌트

LOT 설정을 트리 구조로 표시하고 콤보박스로 값을 변경하는 컴포넌트
"""
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QComboBox, QVBoxLayout,
    QHBoxLayout, QLabel, QSizePolicy, QStyledItemDelegate
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from ..core import ComponentBase, LayoutSystem, Theme
from ..utils import IconProvider


class ComboBoxDelegate(QStyledItemDelegate):
    """트리 아이템에 콤보박스를 표시하는 델리게이트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items_data = {}  # {row: [options]}

    def createEditor(self, parent, option, index):
        """에디터 생성 (콤보박스)"""
        if index.column() == 1:  # 값 컬럼
            combo = QComboBox(parent)
            combo.setFixedHeight(LayoutSystem.INPUT_HEIGHT)

            # 해당 행의 옵션 가져오기
            row = index.row()
            if row in self.items_data:
                combo.addItems(self.items_data[row])

            return combo
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """에디터에 데이터 설정"""
        if isinstance(editor, QComboBox):
            value = index.data(Qt.ItemDataRole.DisplayRole)
            idx = editor.findText(value)
            if idx >= 0:
                editor.setCurrentIndex(idx)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        """모델에 데이터 저장"""
        if isinstance(editor, QComboBox):
            value = editor.currentText()
            model.setData(index, value, Qt.ItemDataRole.DisplayRole)
        else:
            super().setModelData(editor, model, index)


class TreeComboWidget(ComponentBase):
    """Tree + ComboBox 위젯

    구조:
        트리 뷰
        ├─ 카테고리 1
        │   ├─ 항목 1-1: [콤보박스]
        │   └─ 항목 1-2: [콤보박스]
        └─ 카테고리 2
            ├─ 항목 2-1: [콤보박스]
            └─ 항목 2-2: [콤보박스]
    """
    value_changed = pyqtSignal(str, str)  # (key, value)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("TreeComboWidget")

        # 데이터 저장
        self.config_data = {}  # {key: {"label": "라벨", "value": "값", "options": [...]}}
        self.tree_items = {}   # {key: QTreeWidgetItem}

        # ========== 수직 레이아웃 ==========
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === 트리 위젯 ===
        self.tree = QTreeWidget()
        self.tree.setObjectName("lot_config_tree")
        self.tree.setHeaderLabels(["항목", "값"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 300)
        self.tree.setMinimumHeight(400)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 스타일 (hover 제거, 선택 시 글자색 개선)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                border: {LayoutSystem.BORDER_WIDTH}px solid {self.theme.colors.GRAY_300};
                border-radius: {LayoutSystem.BORDER_RADIUS}px;
                background-color: {self.theme.colors.WHITE};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QTreeWidget::item {{
                height: 40px;
                padding: 8px;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.theme.colors.PRIMARY_LIGHT};
                color: {self.theme.colors.GRAY_900};
            }}
            QTreeWidget::item:focus {{
                background-color: {self.theme.colors.PRIMARY_LIGHT};
                color: {self.theme.colors.GRAY_900};
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {self.theme.colors.GRAY_100};
                color: {self.theme.colors.GRAY_700};
                font-weight: {self.theme.fonts.SEMIBOLD};
                font-size: {self.theme.fonts.BODY}px;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {self.theme.colors.GRAY_300};
            }}
        """)

        # 아이템 변경 시그널 연결
        self.tree.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self.tree, 1)  # stretch=1

    def add_category(self, title, icon_type=None):
        """카테고리 추가

        Args:
            title: 카테고리 제목
            icon_type: 아이콘 타입 ("document", "settings", "factory")
        """
        category_item = QTreeWidgetItem(self.tree)
        category_item.setText(0, title)
        category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        category_item.setFirstColumnSpanned(True)

        # 카테고리 스타일
        font = category_item.font(0)
        font.setPointSize(self.theme.fonts.H3)
        font.setWeight(self.theme.fonts.SEMIBOLD)
        category_item.setFont(0, font)
        category_item.setForeground(0, QColor(self.theme.colors.GRAY_900))

        # SVG 아이콘 설정
        if icon_type:
            icon = IconProvider.get_icon(icon_type, size=20, color=self.theme.colors.GRAY_700)
            category_item.setIcon(0, icon)

        return category_item

    def add_config_item(self, category_item, key, label, value, options):
        """설정 항목 추가

        Args:
            category_item: 부모 카테고리 아이템
            key: 설정 키 (예: "model_code")
            label: 표시 라벨 (예: "모델명 코드")
            value: 현재 값 (예: "P10")
            options: 선택 가능한 옵션 리스트 (예: ["P10", "W10", "M10"])
        """
        item = QTreeWidgetItem(category_item)
        item.setText(0, label)
        item.setText(1, value)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(0, Qt.ItemDataRole.UserRole, key)  # key 저장
        item.setData(1, Qt.ItemDataRole.UserRole, options)  # options 저장

        # 데이터 저장
        self.config_data[key] = {
            "label": label,
            "value": value,
            "options": options,
            "item": item
        }
        self.tree_items[key] = item

        # 값 컬럼에 콤보박스 생성
        combo = QComboBox()
        combo.setObjectName(f"combo_{key}")
        combo.addItems(options)
        combo.setCurrentText(value)
        combo.setFixedHeight(LayoutSystem.INPUT_HEIGHT - 8)  # 트리 아이템에 맞게 조정
        combo.currentTextChanged.connect(lambda v: self._on_combo_changed(key, v))

        self.tree.setItemWidget(item, 1, combo)

        return item

    def _on_combo_changed(self, key, value):
        """콤보박스 값 변경"""
        if key in self.config_data:
            self.config_data[key]["value"] = value
            self.value_changed.emit(key, value)

    def _on_item_changed(self, item, column):
        """트리 아이템 변경"""
        if column == 1:  # 값 컬럼
            key = item.data(0, Qt.ItemDataRole.UserRole)
            if key and key in self.config_data:
                new_value = item.text(1)
                self.config_data[key]["value"] = new_value
                self.value_changed.emit(key, new_value)

    def get_config(self):
        """현재 설정값 가져오기"""
        return {key: data["value"] for key, data in self.config_data.items()}

    def set_value(self, key, value):
        """특정 키의 값 설정"""
        if key in self.config_data:
            self.config_data[key]["value"] = value
            item = self.config_data[key]["item"]

            # 아이템 위젯(콤보박스) 찾아서 업데이트
            combo = self.tree.itemWidget(item, 1)
            if combo and isinstance(combo, QComboBox):
                combo.setCurrentText(value)

    def expand_all(self):
        """모든 카테고리 펼치기"""
        self.tree.expandAll()

    def collapse_all(self):
        """모든 카테고리 접기"""
        self.tree.collapseAll()
