"""미니멀 통계 카드 컴포넌트

2025 하이퍼 미니멀리즘 트렌드 적용
- 큰 숫자 중심
- 작은 라벨
- 미세한 그림자
- 부드러운 호버 효과
"""
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from ..core import ComponentBase, Theme


class StatCard(ComponentBase):
    """미니멀 통계 카드

    구조:
        큰 숫자 (48px, Bold, Center)
        작은 라벨 (12px, Gray, Center)
    """

    def __init__(self, label_text, value_text="0", theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName(f"StatCard_{label_text.replace(' ', '_')}")

        # 고정 크기
        self.setFixedHeight(120)
        self.setMinimumWidth(150)

        # 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 숫자 (메인)
        self.value_label = QLabel(value_text)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: {self.theme.fonts.BOLD};
            font-family: {self.theme.fonts.FAMILY_MONO};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        layout.addWidget(self.value_label)

        # 라벨 (하단)
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            font-size: {self.theme.fonts.CAPTION}px;
            font-weight: {self.theme.fonts.MEDIUM};
            color: {self.theme.colors.GRAY_600};
            background: transparent;
        """)
        layout.addWidget(label)

        # 카드 스타일
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_200};
                border-radius: 12px;
            }}
        """)

        # 미세한 그림자
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # 호버 애니메이션 준비 (y 위치 조정용)
        self._y_offset = 0

    def set_value(self, text, color=None):
        """값 업데이트"""
        self.value_label.setText(text)
        if color:
            self.value_label.setStyleSheet(
                self.value_label.styleSheet().replace(
                    self.theme.colors.GRAY_900, color
                )
            )

    def enterEvent(self, event):
        """마우스 진입 시 - 살짝 위로"""
        # 그림자 강화
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # 테두리 색상 변경
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.PRIMARY_LIGHT};
                border-radius: 12px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """마우스 벗어날 때 - 원래대로"""
        # 그림자 원복
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # 테두리 색상 원복
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_200};
                border-radius: 12px;
            }}
        """)
        super().leaveEvent(event)
