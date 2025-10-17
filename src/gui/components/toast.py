"""토스트 알림 컴포넌트

가운데 상단에서 부드럽게 나타났다가 자동으로 사라지는 알림
"""
from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor
from ..core import ComponentBase, Theme


class Toast(ComponentBase):
    """토스트 알림

    화면 중앙 상단에서 나타났다가 자동으로 사라지는 알림
    """

    def __init__(self, parent, theme=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # 메시지 레이블
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(300)
        self.label.setMaximumWidth(500)

        # 투명도 효과
        self.opacity_effect = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(self.opacity_effect)

        # 자동 닫기 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self._fade_out)

        # 애니메이션
        self.fade_in_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.fade_out_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.fade_out_animation.finished.connect(self.close)

    def show_success(self, message, duration=3000):
        """성공 메시지 표시

        Args:
            message: 메시지 내용
            duration: 표시 시간 (ms, 기본 3초)
        """
        self._show(message, "success", duration)

    def show_error(self, message, duration=4000):
        """에러 메시지 표시

        Args:
            message: 메시지 내용
            duration: 표시 시간 (ms, 기본 4초)
        """
        self._show(message, "error", duration)

    def show_info(self, message, duration=3000):
        """정보 메시지 표시

        Args:
            message: 메시지 내용
            duration: 표시 시간 (ms, 기본 3초)
        """
        self._show(message, "info", duration)

    def _show(self, message, toast_type, duration):
        """토스트 표시

        Args:
            message: 메시지
            toast_type: "success", "error", "info"
            duration: 표시 시간 (ms)
        """
        # 스타일 설정
        if toast_type == "success":
            bg_color = self.theme.colors.SUCCESS
            icon = "✓"
        elif toast_type == "error":
            bg_color = self.theme.colors.ERROR
            icon = "✗"
        else:
            bg_color = self.theme.colors.PRIMARY
            icon = "ℹ"

        self.label.setText(f"{icon}  {message}")
        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {self.theme.colors.WHITE};
                font-size: {self.theme.fonts.BODY}px;
                font-weight: {self.theme.fonts.MEDIUM};
                padding: 16px 24px;
                border-radius: 8px;
            }}
        """)

        # 크기 조정
        self.label.adjustSize()
        self.setFixedSize(self.label.size())

        # 위치 설정 (부모 중앙 상단)
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = 80  # 상단에서 80px 아래
            self.move(x, y)

        # Fade in 애니메이션
        self.opacity_effect.setOpacity(0.0)
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 표시
        self.show()
        self.fade_in_animation.start()

        # 자동 닫기 타이머 시작
        self.timer.start(duration)

    def _fade_out(self):
        """Fade out 애니메이션"""
        self.timer.stop()

        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.start()


class ToastManager:
    """토스트 관리자

    여러 토스트를 관리하고 표시
    """

    def __init__(self, parent, theme=None):
        self.parent = parent
        self.theme = theme or Theme()
        self.active_toasts = []

    def show_success(self, message, duration=3000):
        """성공 토스트 표시"""
        toast = Toast(self.parent, self.theme)
        toast.show_success(message, duration)
        self.active_toasts.append(toast)
        toast.destroyed.connect(lambda: self._remove_toast(toast))

    def show_error(self, message, duration=4000):
        """에러 토스트 표시"""
        toast = Toast(self.parent, self.theme)
        toast.show_error(message, duration)
        self.active_toasts.append(toast)
        toast.destroyed.connect(lambda: self._remove_toast(toast))

    def show_info(self, message, duration=3000):
        """정보 토스트 표시"""
        toast = Toast(self.parent, self.theme)
        toast.show_info(message, duration)
        self.active_toasts.append(toast)
        toast.destroyed.connect(lambda: self._remove_toast(toast))

    def _remove_toast(self, toast):
        """토스트 제거"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
