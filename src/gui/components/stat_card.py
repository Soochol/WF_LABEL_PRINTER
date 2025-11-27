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
        self.setObjectName("StatCard")  # QSS 셀렉터 매칭용 고정 이름

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
        self.value_label.setProperty("data-role", "value")  # QSS 셀렉터용
        layout.addWidget(self.value_label)

        # 라벨 (하단)
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("data-role", "title")  # QSS 셀렉터용
        layout.addWidget(label)

        # 미세한 그림자
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # 호버 애니메이션 준비 (y 위치 조정용)
        self._y_offset = 0

    def set_value(self, text, color=None):
        """값 업데이트

        Args:
            text: 표시할 값
            color: 색상 키 ("success", "error", "primary", "muted") 또는 None
        """
        self.value_label.setText(text)
        if color:
            # QSS property로 색상 지정 (data-color 속성 사용)
            self.value_label.setProperty("data-color", color)
            self.value_label.style().unpolish(self.value_label)
            self.value_label.style().polish(self.value_label)

    def enterEvent(self, event):
        """마우스 진입 시 - 그림자 강화"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """마우스 벗어날 때 - 그림자 원복"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        super().leaveEvent(event)
