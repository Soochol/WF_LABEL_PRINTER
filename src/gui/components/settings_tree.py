"""설정 트리 네비게이션 (VSCode 스타일)"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import Theme

class SettingsTree(QTreeWidget):
    """설정 트리 네비게이션"""

    category_selected = pyqtSignal(str, str)  # (category_id, category_name)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 트리 설정
        self.setHeaderHidden(True)  # 헤더 숨김
        self.setIndentation(20)  # 들여쓰기
        self.setAnimated(True)  # 애니메이션
        self.setExpandsOnDoubleClick(False)  # 더블클릭 확장 비활성화

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

        # 초기 선택 (첫 번째 항목)
        first_item = self.topLevelItem(0)
        if first_item and first_item.childCount() > 0:
            first_child = first_item.child(0)
            self.setCurrentItem(first_child)
            self._on_item_clicked(first_child, 0)

    def _build_tree(self):
        """트리 구조 생성"""
        # 하드웨어
        hardware = QTreeWidgetItem(self, ["하드웨어"])
        hardware.setExpanded(True)

        printer = QTreeWidgetItem(hardware, ["프린터"])
        printer.setData(0, Qt.ItemDataRole.UserRole, "hardware.printer")

        serial = QTreeWidgetItem(hardware, ["시리얼 포트"])
        serial.setData(0, Qt.ItemDataRole.UserRole, "hardware.serial")

        # 출력
        output = QTreeWidgetItem(self, ["출력"])
        output.setExpanded(True)

        automation = QTreeWidgetItem(output, ["자동화"])
        automation.setData(0, Qt.ItemDataRole.UserRole, "output.automation")

        # 시스템
        system = QTreeWidgetItem(self, ["시스템"])
        system.setExpanded(True)

        backup = QTreeWidgetItem(system, ["백업"])
        backup.setData(0, Qt.ItemDataRole.UserRole, "system.backup")

    def _on_item_clicked(self, item, column):
        """트리 항목 클릭"""
        # 카테고리 ID 가져오기
        category_id = item.data(0, Qt.ItemDataRole.UserRole)

        if category_id:
            category_name = item.text(0)
            self.category_selected.emit(category_id, category_name)
