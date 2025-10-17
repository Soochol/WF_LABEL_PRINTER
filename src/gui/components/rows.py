"""모든 Row 컴포넌트

체크리스트 준수:
- ✅ 레이아웃 매니저만 사용 (setGeometry 없음)
- ✅ 모든 위젯 즉시 addWidget 호출
- ✅ stretch factor 명시
- ✅ 고정 크기 명시적 설정
- ✅ 간격 및 여백 설정
- ✅ objectName 설정 (디버깅용)
"""
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from ..core import RowBase, LayoutSystem, Theme

class FormRow(RowBase):
    """레이블 + 위젯 행 (일반용)

    구조: [Label(고정 140px)] + [Widget(확장)]
    """
    def __init__(self, label_text, widget, theme=None, parent=None):
        super().__init__(parent)
        theme = theme or Theme()
        self.setObjectName(f"FormRow_{label_text.replace(' ', '_')}")

        # ========== 수평 레이아웃 (60px 고정 높이) ==========
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음
        layout.setSpacing(LayoutSystem.SPACING_ITEM)  # 12px 간격

        # === 레이블 영역 (고정 너비) ===
        label = QLabel(label_text)
        label.setObjectName(f"label_{label_text.replace(' ', '_')}")
        label.setFixedWidth(LayoutSystem.LABEL_WIDTH)  # 140px 고정
        label.setStyleSheet(f"font-weight:{theme.fonts.MEDIUM}; color:{theme.colors.GRAY_700};")
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # === 위젯 영역 (확장) ===
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(widget, 1)  # stretch=1로 확장

        self.widget = widget

class SelectRow(RowBase):
    """레이블 + Combobox 행

    구조: [Label(고정 140px)] + [ComboBox(확장, 48px 높이)]
    """
    value_changed = pyqtSignal(str)

    def __init__(self, label_text, options, default="", theme=None, parent=None):
        super().__init__(parent)
        theme = theme or Theme()
        self.setObjectName(f"SelectRow_{label_text.replace(' ', '_')}")

        # ========== 수평 레이아웃 (60px 고정 높이) ==========
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음
        layout.setSpacing(LayoutSystem.SPACING_ITEM)  # 12px 간격

        # === 레이블 영역 (고정 너비) ===
        label = QLabel(label_text)
        label.setObjectName(f"label_{label_text.replace(' ', '_')}")
        label.setFixedWidth(LayoutSystem.LABEL_WIDTH)  # 140px 고정
        label.setStyleSheet(f"font-weight:{theme.fonts.MEDIUM}; color:{theme.colors.GRAY_700};")
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # === ComboBox 영역 (확장) ===
        self.combo = QComboBox()
        self.combo.setObjectName(f"combo_{label_text.replace(' ', '_')}")
        self.combo.addItems(options)
        if default: self.combo.setCurrentText(default)
        self.combo.setFixedHeight(LayoutSystem.INPUT_HEIGHT)  # 48px 고정
        self.combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo.currentTextChanged.connect(self.value_changed.emit)
        layout.addWidget(self.combo, 1)  # stretch=1로 확장

    def get_value(self): return self.combo.currentText()
    def set_value(self, v):
        idx = self.combo.findText(v)
        if idx >= 0: self.combo.setCurrentIndex(idx)

class InputRow(RowBase):
    """레이블 + Input 행

    구조: [Label(고정 140px)] + [QLineEdit(확장, 48px 높이)]
    """
    text_changed = pyqtSignal(str)

    def __init__(self, label_text, placeholder="", default="", monospace=False, theme=None, parent=None):
        super().__init__(parent)
        theme = theme or Theme()
        self.setObjectName(f"InputRow_{label_text.replace(' ', '_')}")

        # ========== 수평 레이아웃 (60px 고정 높이) ==========
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음
        layout.setSpacing(LayoutSystem.SPACING_ITEM)  # 12px 간격

        # === 레이블 영역 (고정 너비) ===
        label = QLabel(label_text)
        label.setObjectName(f"label_{label_text.replace(' ', '_')}")
        label.setFixedWidth(LayoutSystem.LABEL_WIDTH)  # 140px 고정
        label.setStyleSheet(f"font-weight:{theme.fonts.MEDIUM}; color:{theme.colors.GRAY_700};")
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # === Input 영역 (확장) ===
        self.input = QLineEdit()
        self.input.setObjectName(f"input_{label_text.replace(' ', '_')}")
        self.input.setPlaceholderText(placeholder)
        if default: self.input.setText(default)
        self.input.setFixedHeight(LayoutSystem.INPUT_HEIGHT)  # 48px 고정
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if monospace: self.input.setStyleSheet(f"font-family:{theme.fonts.FAMILY_MONO};")
        self.input.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self.input, 1)  # stretch=1로 확장

    def get_value(self): return self.input.text()
    def set_value(self, t): self.input.setText(t)

class DisplayRow(RowBase):
    """레이블 + 읽기전용 값 행

    구조: [Icon Badge] + [Label(고정 140px)] + [ValueLabel(확장)]
    """
    def __init__(
        self,
        label_text,
        value_text="",
        icon="",
        badge_color=None,
        theme=None,
        parent=None
    ):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName(f"DisplayRow_{label_text.replace(' ', '_')}")

        # ========== 수평 레이아웃 (60px 고정 높이) ==========
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음
        layout.setSpacing(LayoutSystem.SPACING_ITEM)  # 12px 간격

        # === 아이콘 배지 (선택사항) ===
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFixedSize(40, 40)
            bg_color = badge_color or self.theme.colors.BADGE_BLUE
            icon_label.setStyleSheet(f"""
                background-color: {bg_color};
                border-radius: 8px;
                font-size: 20px;
                padding: 8px;
            """)
            icon_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            layout.addWidget(
                icon_label, 0, Qt.AlignmentFlag.AlignVCenter
            )

        # === 레이블 영역 (고정 너비) ===
        label = QLabel(label_text)
        label.setObjectName(f"label_{label_text.replace(' ', '_')}")
        label.setFixedWidth(LayoutSystem.LABEL_WIDTH)  # 140px 고정
        label.setStyleSheet(
            f"font-weight:{self.theme.fonts.MEDIUM}; "
            f"color:{self.theme.colors.GRAY_700};"
        )
        layout.addWidget(
            label, 0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # === 값 영역 (확장, 읽기전용) ===
        self.value_label = QLabel(value_text)
        self.value_label.setObjectName(f"value_{label_text.replace(' ', '_')}")
        self._update_style()
        self.value_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(
            self.value_label, 1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

    def _update_style(self, color=None):
        """스타일 업데이트 (색상 커스터마이징 가능)"""
        color = color or self.theme.colors.PRIMARY
        self.value_label.setStyleSheet(
            f"font-size:{self.theme.fonts.H2}px; "
            f"font-weight:{self.theme.fonts.BOLD}; "
            f"font-family:{self.theme.fonts.FAMILY_MONO}; "
            f"color:{color};"
        )

    def set_value(self, t, color=None):
        """값 설정 (선택적으로 색상 지정 가능)"""
        self.value_label.setText(t)
        if color:
            self._update_style(color)

class ButtonRow(RowBase):
    """버튼 자동 정렬 행

    구조: [Stretch(옵션)] + [Button...] (align에 따라 좌/중/우 정렬)
    """
    def __init__(self, align="right", theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName(f"ButtonRow_{align}")

        # ========== 수평 레이아웃 (60px 고정 높이) ==========
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음
        self.layout.setSpacing(LayoutSystem.SPACING_BUTTON)  # 8px 간격

        # === 정렬 설정 (Stretch 사용) ===
        if align == "right":
            self.layout.addStretch()  # 좌측에 stretch 추가 -> 버튼이 우측으로
        elif align == "center":
            self.layout.addStretch()  # 양쪽에 stretch 추가 -> 버튼이 중앙으로

    def add_primary(self, text, callback=None, width=None):
        """Primary 버튼 추가 (파란색, 주요 액션)"""
        btn = QPushButton(text)
        btn.setObjectName(f"primary_btn_{text.replace(' ', '_')}")
        btn.setProperty("primary", True)
        btn.setFixedHeight(LayoutSystem.BUTTON_HEIGHT)  # 44px 고정
        btn.setFixedWidth(width or LayoutSystem.BUTTON_PRIMARY_WIDTH)  # 140px 기본
        btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if callback: btn.clicked.connect(callback)
        self.layout.addWidget(btn, 0)  # stretch=0 (고정)
        return btn

    def add_secondary(self, text, callback=None, width=None):
        """Secondary 버튼 추가 (회색, 보조 액션)"""
        btn = QPushButton(text)
        btn.setObjectName(f"secondary_btn_{text.replace(' ', '_')}")
        btn.setProperty("secondary", True)
        btn.setFixedHeight(LayoutSystem.BUTTON_HEIGHT)  # 44px 고정
        btn.setFixedWidth(width or LayoutSystem.BUTTON_MIN_WIDTH)  # 100px 기본
        btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if callback: btn.clicked.connect(callback)
        self.layout.addWidget(btn, 0)  # stretch=0 (고정)
        return btn
