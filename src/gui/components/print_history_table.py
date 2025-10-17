"""출력 이력 테이블 컴포넌트"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from ..core import ComponentBase, LayoutSystem, Theme


class PrintHistoryTable(ComponentBase):
    """출력 이력 테이블

    4개 컬럼: 시간 | 시리얼 번호 | MAC 주소 | 상태
    """

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 테이블 위젯 생성
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "시간", "시리얼 번호", "MAC 주소", "상태"
        ])

        # 테이블 스타일 (보더리스 미니멀)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {self.theme.colors.GRAY_200};
                background-color: {self.theme.colors.WHITE};
                gridline-color: transparent;
                font-size: {self.theme.fonts.BODY}px;
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 16px 12px;
                color: {self.theme.colors.GRAY_900};
                border: none;
                border-bottom: 1px solid {self.theme.colors.GRAY_100};
            }}
            QTableWidget::item:hover {{
                background-color: {self.theme.colors.GRAY_50};
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.colors.PRIMARY_LIGHT};
                color: {self.theme.colors.PRIMARY_DARK};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {self.theme.colors.GRAY_700};
                font-weight: {self.theme.fonts.SEMIBOLD};
                font-size: {self.theme.fonts.CAPTION}px;
                text-transform: uppercase;
                padding: 12px;
                border: none;
                border-bottom: 1px solid {self.theme.colors.GRAY_200};
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme.colors.GRAY_300};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.theme.colors.GRAY_400};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        # 테이블 설정
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        # 읽기 전용 설정 (수정 불가)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 포커스 제거 (클릭 시 포커스 표시 안 함)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 고정 높이
        self.table.setFixedHeight(350)

        # 열 너비 설정 - 모든 열 크기 조절 가능
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # 모든 열 마우스로 크기 조절 가능
        header.resizeSection(0, 150)  # 시간 초기 크기
        header.resizeSection(1, 300)  # 시리얼 번호 초기 크기
        header.resizeSection(2, 300)  # MAC 주소 초기 크기
        header.resizeSection(3, 100)  # 상태 초기 크기

        # 레이아웃에 테이블 추가
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

    def set_history(self, history_list):
        """이력 데이터 설정

        Args:
            history_list: [
                {
                    'print_datetime': '2025-10-17T19:35:48.738152',
                    'serial_number': 'P10DL0S0H3A00C100011',
                    'mac_address': 'PSAD0CF1327829495',
                    'status': 'success'
                },
                ...
            ]
        """
        self.table.setRowCount(0)

        for record in history_list:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 시간 (HH:MM:SS 형식으로 변환)
            datetime_str = record.get('print_datetime', '')
            time_str = ''
            if datetime_str:
                try:
                    # '2025-10-17T19:35:48.738152' -> '19:35:48'
                    time_str = datetime_str.split('T')[1].split('.')[0]
                except:
                    time_str = datetime_str

            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, time_item)

            # 시리얼 번호
            serial_item = QTableWidgetItem(record.get('serial_number', ''))
            self.table.setItem(row_idx, 1, serial_item)

            # MAC 주소 (전체 표시)
            mac_address = record.get('mac_address', '')
            mac_item = QTableWidgetItem(mac_address)
            self.table.setItem(row_idx, 2, mac_item)

            # 상태 (미니멀 - 점 + 텍스트)
            status = record.get('status', '')
            if status == 'success':
                status_display = "\u2022 \uc131\uacf5"
                status_color = self.theme.colors.SUCCESS
            elif status == 'failed':
                status_display = "\u2022 \uc2e4\ud328"
                status_color = self.theme.colors.ERROR
            else:
                status_display = "-"
                status_color = self.theme.colors.GRAY_500

            status_item = QTableWidgetItem(status_display)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QBrush(QColor(status_color)))

            self.table.setItem(row_idx, 3, status_item)
