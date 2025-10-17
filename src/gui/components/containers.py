"""컨테이너 컴포넌트

체크리스트 준수:
- ✅ 레이아웃 매니저만 사용
- ✅ 모든 위젯 addWidget으로 추가
- ✅ stretch factor 및 alignment 명시
- ✅ 간격 및 여백 설정
- ✅ objectName 설정
"""
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ..core import ComponentBase, LayoutSystem, Theme

class Section(ComponentBase):
    """섹션 컨테이너 - 제목 + 여러 행

    구조:
        Title (24px 고정 높이, 옵션)
        ↓ 16px 간격
        Row 1 (60px 고정)
        ↓ 16px 간격
        Row 2 (60px 고정)
        ...
    """
    def __init__(self, title, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName(f"Section_{title.replace(' ', '_') if title else 'NoTitle'}")

        # ========== 수직 레이아웃 ==========
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 여백 없음 (Card가 관리)
        self.layout.setSpacing(LayoutSystem.SPACING_ROW)  # 16px 간격

        # === 제목 영역 (옵션) ===
        if title:
            title_label = QLabel(title.upper())  # 대문자 변환
            title_label.setObjectName(f"title_{title.replace(' ', '_')}")
            title_label.setFixedHeight(LayoutSystem.LABEL_HEIGHT)  # 24px 고정
            title_label.setStyleSheet(f"""
                font-size: {self.theme.fonts.CAPTION}px;
                font-weight: {self.theme.fonts.SEMIBOLD};
                color: {self.theme.colors.GRAY_700};
                letter-spacing: 0.5px;
            """)
            title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def add_row(self, row):
        """Row 컴포넌트 추가"""
        self.layout.addWidget(row, 0)  # stretch=0 (고정 크기)
        return row

    def add_spacing(self, height=None):
        """추가 간격 (기본 16px)"""
        self.layout.addSpacing(height or LayoutSystem.SPACING_ROW)

class Card(ComponentBase):
    """카드 컨테이너 - 배경 + 패딩 + 여러 섹션

    구조:
        24px 패딩
        ┌───────────────────────┐
        │ Section 1             │
        │ ↓ 32px 간격           │
        │ Section 2             │
        │ ↓ 32px 간격           │
        │ Section 3             │
        └───────────────────────┘
        24px 패딩
    """
    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("Card")

        # ========== 수직 레이아웃 ==========
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            LayoutSystem.PADDING_CARD,  # 24px
            LayoutSystem.PADDING_CARD,  # 24px
            LayoutSystem.PADDING_CARD,  # 24px
            LayoutSystem.PADDING_CARD   # 24px
        )
        self.layout.setSpacing(LayoutSystem.SPACING_SECTION)  # 32px 간격

        # === 카드 스타일 (흰색 배경, 회색 테두리, 둥근 모서리) ===
        self.setStyleSheet(f"""
            Card {{
                background-color: {self.theme.colors.WHITE};
                border: {LayoutSystem.BORDER_WIDTH}px solid {self.theme.colors.GRAY_200};
                border-radius: {LayoutSystem.BORDER_RADIUS + 2}px;
            }}
        """)

        # === 드롭 섀도우 효과 (현대적 느낌, 강화) ===
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)  # 블러 반경 증가
        shadow.setColor(QColor(0, 0, 0, 30))  # 검은색, 투명도 증가
        shadow.setOffset(0, 2)  # Y축으로 2px 오프셋
        self.setGraphicsEffect(shadow)

    def add_section(self, section):
        """Section 추가 (고정 크기)"""
        self.layout.addWidget(section, 0)  # stretch=0 (섹션 내부 Row들이 고정 크기)
        return section

    def add_widget(self, widget):
        """일반 위젯 추가 (확장 가능)"""
        self.layout.addWidget(widget, 1)  # stretch=1 (확장 가능)
        return widget

    def add_stretch(self):
        """늘어나는 공간 추가 (남은 공간 채움)"""
        self.layout.addStretch(1)
