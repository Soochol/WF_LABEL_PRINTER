"""상태바 컴포넌트 - 프린터/MCU 연결 상태 표시"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ..core import Theme

class StatusBar(QWidget):
    """하단 상태바 - 연결 상태 표시"""

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("StatusBar")  # QSS 셀렉터용
        self.setFixedHeight(32)

        # 레이아웃
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(24)

        # 프린터 상태
        self.printer_label = QLabel("프린터: 확인 중...")
        layout.addWidget(self.printer_label)

        # 구분선
        separator = QLabel("|")
        separator.setProperty("data-role", "separator")
        layout.addWidget(separator)

        # MCU 상태
        self.mcu_label = QLabel("MCU: 확인 중...")
        layout.addWidget(self.mcu_label)

        layout.addStretch()

    def set_printer_status(self, status: str, detail: str = ""):
        """
        프린터 상태 설정

        Args:
            status: "connected", "disconnected", "checking"
            detail: 추가 정보 (예: 프린터 이름)
        """
        if status == "connected":
            icon = "✓"
            color = self.theme.colors.SUCCESS
            text = f"프린터: {icon} 연결됨"
            if detail:
                text += f" ({detail})"
        elif status == "disconnected":
            icon = "✗"
            color = self.theme.colors.ERROR
            text = f"프린터: {icon} 연결 안 됨"
        else:  # checking
            icon = "🔄"
            color = self.theme.colors.GRAY_600
            text = f"프린터: {icon} 확인 중..."

        self.printer_label.setText(text)
        # 동적 색상은 인라인 스타일 유지
        self.printer_label.setStyleSheet(f"color: {color};")

    def set_mcu_status(self, status: str, detail: str = ""):
        """
        MCU 상태 설정

        Args:
            status: "connected", "disconnected", "reconnecting", "checking"
            detail: 추가 정보 (예: COM5)
        """
        if status == "connected":
            icon = "✓"
            color = self.theme.colors.SUCCESS
            text = f"MCU: {icon} 연결됨"
            if detail:
                text += f" ({detail})"
        elif status == "disconnected":
            icon = "✗"
            color = self.theme.colors.ERROR
            text = f"MCU: {icon} 연결 안 됨"
        elif status == "reconnecting":
            icon = "🔄"
            color = self.theme.colors.GRAY_600
            text = f"MCU: {icon} 재연결 중..."
            if detail:
                text += f" ({detail})"
        else:  # checking
            icon = "🔄"
            color = self.theme.colors.GRAY_600
            text = f"MCU: {icon} 확인 중..."

        self.mcu_label.setText(text)
        # 동적 색상은 인라인 스타일 유지
        self.mcu_label.setStyleSheet(f"color: {color};")