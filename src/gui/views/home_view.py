"""홈 화면 - 하이퍼 미니멀리즘 디자인"""
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from ..core import ComponentBase, LayoutSystem, Theme
from ..components import StatCard, PrintHistoryTable

class HomeView(ComponentBase):
    """홈 뷰 - 대시보드"""
    reset_clicked = pyqtSignal()
    print_requested = pyqtSignal()
    test_requested = pyqtSignal()

    def __init__(self, theme=None, parent=None):
        super().__init__()
        self.theme = theme or Theme()

        # 배경색 (미세한 회색)
        self.setStyleSheet(f"""
            HomeView {{
                background-color: {self.theme.colors.GRAY_50};
            }}
        """)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(32)

        # ========== 헤더 (심플) ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # 타이틀
        title = QLabel("Zebra Label Printer")
        title.setStyleSheet(f"""
            font-size: {self.theme.fonts.H1}px;
            font-weight: {self.theme.fonts.BOLD};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # 새로고침 버튼
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.WHITE};
                color: {self.theme.colors.GRAY_700};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: {self.theme.fonts.MEDIUM};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.GRAY_50};
                border-color: {self.theme.colors.GRAY_400};
            }}
        """)
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._on_reset)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # ========== 통계 카드 3개 (가로 배치) ==========
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.today_card = StatCard("오늘 출력", "0", theme=self.theme)
        self.success_card = StatCard("성공", "0", theme=self.theme)
        self.failed_card = StatCard("실패", "0", theme=self.theme)

        stats_layout.addWidget(self.today_card)
        stats_layout.addWidget(self.success_card)
        stats_layout.addWidget(self.failed_card)
        stats_layout.addStretch()

        main_layout.addLayout(stats_layout)

        # ========== 시리얼 번호 패널 (간소화) ==========
        serial_panel = ComponentBase()
        serial_panel.setStyleSheet(f"""
            ComponentBase {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_200};
                border-radius: 8px;
                padding: 20px;
            }}
        """)

        serial_layout = QVBoxLayout(serial_panel)
        serial_layout.setContentsMargins(20, 20, 20, 20)
        serial_layout.setSpacing(12)

        # 마지막 출력
        last_row = QHBoxLayout()
        last_label = QLabel("마지막 출력")
        last_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.MEDIUM};
            color: {self.theme.colors.GRAY_600};
            background: transparent;
        """)
        last_label.setFixedWidth(100)
        last_row.addWidget(last_label)

        self.last_serial_label = QLabel("-")
        self.last_serial_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.REGULAR};
            font-family: {self.theme.fonts.FAMILY_MONO};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        last_row.addWidget(self.last_serial_label)
        last_row.addStretch()
        serial_layout.addLayout(last_row)

        # 다음 시리얼
        next_row = QHBoxLayout()
        next_label = QLabel("다음 시리얼")
        next_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.MEDIUM};
            color: {self.theme.colors.GRAY_600};
            background: transparent;
        """)
        next_label.setFixedWidth(100)
        next_row.addWidget(next_label)

        self.next_serial_label = QLabel("-")
        self.next_serial_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.REGULAR};
            font-family: {self.theme.fonts.FAMILY_MONO};
            color: {self.theme.colors.PRIMARY};
            background: transparent;
        """)
        next_row.addWidget(self.next_serial_label)
        next_row.addStretch()
        serial_layout.addLayout(next_row)

        # 감지된 MAC
        mac_row = QHBoxLayout()
        mac_label = QLabel("감지된 MAC")
        mac_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.MEDIUM};
            color: {self.theme.colors.GRAY_600};
            background: transparent;
        """)
        mac_label.setFixedWidth(100)
        mac_row.addWidget(mac_label)

        self.mac_address_label = QLabel("대기 중...")
        self.mac_address_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.BODY}px;
            font-weight: {self.theme.fonts.REGULAR};
            font-family: {self.theme.fonts.FAMILY_MONO};
            color: {self.theme.colors.GRAY_500};
            background: transparent;
        """)
        mac_row.addWidget(self.mac_address_label)
        mac_row.addStretch()
        serial_layout.addLayout(mac_row)

        # 인쇄 버튼 추가
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # 테스트 인쇄 버튼
        test_btn = QPushButton("테스트 인쇄")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.WHITE};
                color: {self.theme.colors.GRAY_700};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: {self.theme.fonts.MEDIUM};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.GRAY_50};
                border-color: {self.theme.colors.GRAY_400};
            }}
        """)
        test_btn.setFixedHeight(44)
        test_btn.setFixedWidth(120)
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
                padding: 10px 20px;
                font-weight: {self.theme.fonts.SEMIBOLD};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors.PRIMARY_DARK};
            }}
        """)
        print_btn.setFixedHeight(44)
        print_btn.setFixedWidth(120)
        print_btn.clicked.connect(self._on_print)
        button_layout.addWidget(print_btn)

        button_layout.addStretch()
        serial_layout.addLayout(button_layout)

        main_layout.addWidget(serial_panel)

        # ========== 출력 기록 테이블 ==========
        # 섹션 타이틀
        table_title = QLabel("출력 기록")
        table_title.setStyleSheet(f"""
            font-size: {self.theme.fonts.H3}px;
            font-weight: {self.theme.fonts.SEMIBOLD};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
            margin-top: 8px;
        """)
        main_layout.addWidget(table_title)

        # 테이블
        self.history_table = PrintHistoryTable(self.theme)
        main_layout.addWidget(self.history_table)

    def _on_reset(self):
        """Reset 버튼 클릭"""
        self.reset_clicked.emit()

    def _on_test(self):
        """테스트 인쇄"""
        self.test_requested.emit()

    def _on_print(self):
        """인쇄 시작"""
        self.print_requested.emit()

    def set_stats(self, today_count, success_count, failed_count):
        """통계 설정"""
        self.today_card.set_value(str(today_count))
        self.success_card.set_value(
            str(success_count), color=self.theme.colors.SUCCESS
        )
        self.failed_card.set_value(
            str(failed_count), color=self.theme.colors.ERROR
        )

    def set_serial_info(self, last_serial, next_serial):
        """시리얼 번호 정보 설정"""
        self.last_serial_label.setText(last_serial)
        self.next_serial_label.setText(next_serial)

    def set_mac_address(self, mac_address):
        """MAC 주소 설정"""
        if mac_address:
            self.mac_address_label.setText(mac_address)
            self.mac_address_label.setStyleSheet(f"""
                font-size: {self.theme.fonts.BODY}px;
                font-weight: {self.theme.fonts.REGULAR};
                font-family: {self.theme.fonts.FAMILY_MONO};
                color: {self.theme.colors.SUCCESS};
                background: transparent;
            """)
        else:
            self.mac_address_label.setText("대기 중...")
            self.mac_address_label.setStyleSheet(f"""
                font-size: {self.theme.fonts.BODY}px;
                font-weight: {self.theme.fonts.REGULAR};
                font-family: {self.theme.fonts.FAMILY_MONO};
                color: {self.theme.colors.GRAY_500};
                background: transparent;
            """)

    def set_history(self, history_list):
        """출력 리스트 설정"""
        self.history_table.set_history(history_list)
