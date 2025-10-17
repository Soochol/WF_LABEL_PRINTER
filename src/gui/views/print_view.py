"""인쇄 화면 - 하이퍼 미니멀리즘 디자인"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import ComponentBase, Theme

class PrintView(ComponentBase):
    """인쇄 뷰"""
    print_requested = pyqtSignal()
    test_requested = pyqtSignal()

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 배경색
        self.setStyleSheet(f"""
            PrintView {{
                background-color: {self.theme.colors.GRAY_50};
            }}
        """)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # ========== 헤더 ==========
        header = QLabel("Label Print")
        header.setStyleSheet(f"""
            font-size: {self.theme.fonts.H1}px;
            font-weight: {self.theme.fonts.BOLD};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        main_layout.addWidget(header)

        # ========== 상태 정보 패널 ==========
        status_panel = ComponentBase()
        status_panel.setStyleSheet(f"""
            ComponentBase {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_200};
                border-radius: 8px;
            }}
        """)

        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(16)

        # 상태 그리드 (2x2)
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(32)

        # 좌측 열
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # 시리얼 번호
        self.serial_label = self._create_status_row(
            "시리얼 번호", "-", left_col
        )

        # MAC 주소
        self.mac_label = self._create_status_row("MAC 주소", "-", left_col)

        # 우측 열
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # 프린터
        self.printer_label = self._create_status_row(
            "프린터", "연결 대기중", right_col
        )

        # MCU
        self.mcu_label = self._create_status_row(
            "MCU", "연결 대기중", right_col
        )

        grid_layout.addLayout(left_col, stretch=1)
        grid_layout.addLayout(right_col, stretch=1)
        status_layout.addLayout(grid_layout)

        main_layout.addWidget(status_panel)

        # ========== 로그 섹션 ==========
        log_title = QLabel("로그")
        log_title.setStyleSheet(f"""
            font-size: {self.theme.fonts.H3}px;
            font-weight: {self.theme.fonts.SEMIBOLD};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
            margin-top: 8px;
        """)
        main_layout.addWidget(log_title)

        # 로그 텍스트
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: {self.theme.fonts.FAMILY_MONO};
                font-size: {self.theme.fonts.MONOSPACE}px;
                background-color: {self.theme.colors.GRAY_900};
                color: {self.theme.colors.GRAY_50};
                border: 1px solid {self.theme.colors.GRAY_700};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        main_layout.addWidget(self.log_text, stretch=1)

        # ========== 버튼 영역 ==========
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        # 테스트 인쇄 버튼
        test_btn = QPushButton("테스트 인쇄")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.WHITE};
                color: {self.theme.colors.GRAY_700};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: {self.theme.fonts.MEDIUM};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.GRAY_50};
                border-color: {self.theme.colors.GRAY_400};
            }}
        """)
        test_btn.setFixedHeight(48)
        test_btn.setFixedWidth(140)
        test_btn.clicked.connect(self._on_test)
        button_layout.addWidget(test_btn)

        # 인쇄 시작 버튼
        print_btn = QPushButton("인쇄 시작")
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.PRIMARY};
                color: {self.theme.colors.WHITE};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: {self.theme.fonts.SEMIBOLD};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.PRIMARY_DARK};
            }}
        """)
        print_btn.setFixedHeight(48)
        print_btn.setFixedWidth(140)
        print_btn.clicked.connect(self._on_print)
        button_layout.addWidget(print_btn)

        main_layout.addLayout(button_layout)

    def _create_status_row(self, label_text, value_text, layout):
        """상태 행 생성 헬퍼"""
        row = QVBoxLayout()
        row.setSpacing(4)

        # 라벨
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            font-size: {self.theme.fonts.CAPTION}px;
            font-weight: {self.theme.fonts.MEDIUM};
            color: {self.theme.colors.GRAY_600};
            background: transparent;
        """)
        row.addWidget(label)

        # 값
        value = QLabel(value_text)
        value.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.REGULAR};
            font-family: {self.theme.fonts.FAMILY_MONO};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        row.addWidget(value)

        layout.addLayout(row)
        return value

    def _on_print(self):
        """인쇄 시작"""
        self.print_requested.emit()

    def _on_test(self):
        """테스트 인쇄"""
        self.test_requested.emit()

    def set_serial(self, serial):
        """시리얼 번호 설정"""
        self.serial_label.setText(serial)

    def set_mac(self, mac):
        """MAC 주소 설정"""
        self.mac_label.setText(mac)

    def set_printer_status(self, status):
        """프린터 상태 설정"""
        self.printer_label.setText(status)

    def set_mcu_status(self, status):
        """MCU 상태 설정"""
        self.mcu_label.setText(status)

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)

    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()
