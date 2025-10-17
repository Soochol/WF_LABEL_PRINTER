"""설정 항목 위젯 (VSCode 스타일)"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import Theme, LayoutSystem

class SettingItemBase(QWidget):
    """설정 항목 베이스 클래스"""
    value_changed = pyqtSignal(str, object)  # (setting_key, value)

    def __init__(self, setting_key, label, description="", help_table=None, theme=None, parent=None):
        super().__init__(parent)
        self.setting_key = setting_key
        self.theme = theme or Theme()

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 16, 0, 16)
        main_layout.setSpacing(8)

        # 레이블
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.SEMIBOLD};
            color: {self.theme.colors.GRAY_900};
        """)
        main_layout.addWidget(label_widget)

        # 입력 필드 컨테이너 (하위 클래스에서 추가)
        self.input_layout = QHBoxLayout()
        self.input_layout.setSpacing(LayoutSystem.SPACING_ITEM)
        main_layout.addLayout(self.input_layout)

        # 설명 텍스트
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                font-size: {self.theme.fonts.CAPTION}px;
                color: {self.theme.colors.GRAY_600};
                line-height: 1.5;
            """)
            main_layout.addWidget(desc_label)

        # 도움말 테이블 (선택사항)
        if help_table:
            self._add_help_table(main_layout, help_table)

    def _add_help_table(self, layout, table_data):
        """도움말 테이블 추가

        Args:
            layout: 추가할 레이아웃
            table_data: dict with 'headers' and 'rows'
                       {'headers': ['Code', 'Model'], 'rows': [['L0', 'L230-A39'], ...]}
        """
        # 테이블 타이틀
        table_title = QLabel("코드 매핑:")
        table_title.setStyleSheet(f"""
            font-size: {self.theme.fonts.CAPTION}px;
            font-weight: {self.theme.fonts.SEMIBOLD};
            color: {self.theme.colors.GRAY_700};
            margin-top: 8px;
        """)
        layout.addWidget(table_title)

        # 테이블 위젯
        table = QTableWidget()
        table.setColumnCount(len(table_data['headers']))
        table.setRowCount(len(table_data['rows']))
        table.setHorizontalHeaderLabels(table_data['headers'])

        # 헤더 설정
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        # 데이터 채우기
        for row_idx, row_data in enumerate(table_data['rows']):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 읽기 전용
                table.setItem(row_idx, col_idx, item)

        # 테이블 높이 자동 조정
        table.setMaximumHeight(table.verticalHeader().length() + table.horizontalHeader().height() + 4)

        # 스타일링
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 4px;
                background-color: {self.theme.colors.WHITE};
                gridline-color: {self.theme.colors.GRAY_200};
                font-size: {self.theme.fonts.CAPTION}px;
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                color: {self.theme.colors.GRAY_800};
            }}
            QHeaderView::section {{
                background-color: {self.theme.colors.GRAY_100};
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid {self.theme.colors.GRAY_300};
                border-right: 1px solid {self.theme.colors.GRAY_300};
                font-weight: {self.theme.fonts.SEMIBOLD};
                color: {self.theme.colors.GRAY_700};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)

        layout.addWidget(table)


class SelectSettingItem(SettingItemBase):
    """드롭다운 선택 설정 항목"""

    def __init__(self, setting_key, label, options, default="", description="", help_table=None, theme=None, parent=None):
        super().__init__(setting_key, label, description, help_table, theme, parent)

        # 콤보박스
        self.combo = QComboBox()

        # options가 딕셔너리인지 리스트인지 확인
        if isinstance(options, dict):
            # 딕셔너리: {value: display_text}
            self.value_map = options  # value -> display_text
            self.display_map = {v: k for k, v in options.items()}  # display_text -> value
            for value, display_text in options.items():
                self.combo.addItem(display_text, value)  # display_text를 보여주고 value를 data로 저장
        else:
            # 리스트: 기존 방식
            self.value_map = None
            self.display_map = None
            self.combo.addItems(options)

        if default:
            self.set_value(default)

        self.combo.setFixedHeight(LayoutSystem.INPUT_HEIGHT)

        # 마우스 휠 이벤트 무시
        self.combo.wheelEvent = lambda event: event.ignore()

        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme.colors.WHITE};
                border: {LayoutSystem.BORDER_WIDTH}px solid {self.theme.colors.GRAY_300};
                border-radius: {LayoutSystem.BORDER_RADIUS}px;
                padding: 0 12px;
                font-size: {self.theme.fonts.BODY}px;
            }}
            QComboBox:hover {{
                border-color: {self.theme.colors.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        self.combo.currentIndexChanged.connect(self._on_value_changed)
        self.input_layout.addWidget(self.combo, 1)

    def _on_value_changed(self, index):
        """값 변경 시 실제 value 전달 (display_text가 아님)"""
        if self.value_map:
            # 딕셔너리 모드: currentData()에서 실제 value 가져오기
            value = self.combo.currentData()
        else:
            # 리스트 모드: currentText() 사용
            value = self.combo.currentText()
        self.value_changed.emit(self.setting_key, value)

    def get_value(self):
        """실제 value 반환 (display_text가 아님)"""
        if self.value_map:
            return self.combo.currentData()
        else:
            return self.combo.currentText()

    def set_value(self, value):
        """value로 항목 선택"""
        if self.value_map:
            # 딕셔너리 모드: value로 인덱스 찾기
            for i in range(self.combo.count()):
                if self.combo.itemData(i) == value:
                    self.combo.setCurrentIndex(i)
                    return
        else:
            # 리스트 모드: 텍스트로 찾기
            idx = self.combo.findText(value)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)


class InputSettingItem(SettingItemBase):
    """텍스트 입력 설정 항목"""

    def __init__(self, setting_key, label, placeholder="", default="", description="", theme=None, parent=None):
        super().__init__(setting_key, label, description, None, theme, parent)

        # 입력 필드
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        if default:
            self.input.setText(default)
        self.input.setFixedHeight(LayoutSystem.INPUT_HEIGHT)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.colors.WHITE};
                border: {LayoutSystem.BORDER_WIDTH}px solid {self.theme.colors.GRAY_300};
                border-radius: {LayoutSystem.BORDER_RADIUS}px;
                padding: 0 12px;
                font-size: {self.theme.fonts.BODY}px;
            }}
            QLineEdit:hover {{
                border-color: {self.theme.colors.PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {self.theme.colors.PRIMARY};
                outline: none;
            }}
        """)
        self.input.textChanged.connect(self._on_value_changed)
        self.input_layout.addWidget(self.input, 1)

    def _on_value_changed(self, value):
        self.value_changed.emit(self.setting_key, value)

    def get_value(self):
        return self.input.text()

    def set_value(self, value):
        self.input.setText(value)


class CheckboxSettingItem(SettingItemBase):
    """체크박스 설정 항목"""

    def __init__(self, setting_key, label, default=False, description="", theme=None, parent=None):
        super().__init__(setting_key, label, description, None, theme, parent)

        # 체크박스
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(default)
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
        """)
        self.checkbox.stateChanged.connect(self._on_value_changed)
        self.input_layout.addWidget(self.checkbox)
        self.input_layout.addStretch()

    def _on_value_changed(self, state):
        value = state == Qt.CheckState.Checked.value
        self.value_changed.emit(self.setting_key, value)

    def get_value(self):
        return self.checkbox.isChecked()

    def set_value(self, value):
        self.checkbox.setChecked(value)


class SelectWithButtonSettingItem(SelectSettingItem):
    """드롭다운 + 버튼 설정 항목"""

    button_clicked = pyqtSignal()

    def __init__(self, setting_key, label, options, button_text, default="", description="", theme=None, parent=None):
        super().__init__(setting_key, label, options, default, description, None, theme, parent)

        # 버튼 추가
        self.button = QPushButton(button_text)
        self.button.setFixedHeight(LayoutSystem.INPUT_HEIGHT)
        self.button.setFixedWidth(120)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.GRAY_100};
                border: {LayoutSystem.BORDER_WIDTH}px solid {self.theme.colors.GRAY_300};
                border-radius: {LayoutSystem.BORDER_RADIUS}px;
                font-size: {self.theme.fonts.BODY}px;
                color: {self.theme.colors.GRAY_700};
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.GRAY_200};
            }}
        """)
        self.button.clicked.connect(self.button_clicked.emit)
        self.input_layout.addWidget(self.button, 0)
