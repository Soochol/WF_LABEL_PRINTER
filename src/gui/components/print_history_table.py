"""출력 이력 테이블 컴포넌트"""
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QVBoxLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from ..core import ComponentBase, Theme
from ..styles import get_theme_manager
from ..styles.theme_manager import ThemeMode


class PrintHistoryTable(ComponentBase):
    """출력 이력 테이블

    4개 컬럼: 시간 | 시리얼 번호 | MAC 주소 | 상태
    테마 변경 시 자동으로 스타일 업데이트
    """

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self._history_data = []

        # 테이블 위젯 생성
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "시간", "시리얼 번호", "MAC 주소", "상태"
        ])

        # 테이블 설정
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(True)

        # 열 너비 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)
        header.resizeSection(3, 80)

        # 행 높이 설정
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

        # 초기 스타일 적용
        self._apply_theme_style()

        # 테마 변경 시그널 연결
        theme_mgr = get_theme_manager()
        theme_mgr.theme_changed.connect(self._on_theme_changed)

    def _apply_theme_style(self):
        """현재 테마에 맞는 스타일 적용"""
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors
        is_dark = theme_mgr.mode == ThemeMode.DARK

        # 다크모드와 라이트모드에서 확실히 보이는 색상 사용
        if is_dark:
            bg_color = "#0D1117"
            alt_bg_color = "#161B22"
            header_bg = "#21262D"
            border_color = "#30363D"
            text_color = "#E6EDF3"
            hover_color = "#30363D"
        else:
            bg_color = "#FFFFFF"
            alt_bg_color = "#F6F8FA"
            header_bg = "#F6F8FA"
            border_color = "#D0D7DE"
            text_color = "#1F2328"
            hover_color = "#EAEEF2"

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_color};
                alternate-background-color: {alt_bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                gridline-color: {border_color};
                color: {text_color};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {border_color};
                color: {text_color};
            }}
            QTableWidget::item:hover {{
                background-color: {hover_color};
            }}
            QTableWidget::item:selected {{
                background-color: {colors.PRIMARY};
                color: #FFFFFF;
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {text_color};
                font-weight: 600;
                font-size: 13px;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {border_color};
                border-right: 1px solid {border_color};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {bg_color};
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.GRAY_400};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.GRAY_500};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

    def _on_theme_changed(self, theme_mode: str):
        """테마 변경 시 스타일 및 데이터 업데이트"""
        self._apply_theme_style()
        # 상태 색상 업데이트를 위해 데이터 다시 설정
        if self._history_data:
            self.set_history(self._history_data)

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
        self._history_data = history_list
        self.table.setRowCount(0)

        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors

        for record in history_list:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 시간 (HH:MM:SS 형식으로 변환)
            datetime_str = record.get('print_datetime', '')
            time_str = ''
            if datetime_str:
                try:
                    time_str = datetime_str.split('T')[1].split('.')[0]
                except Exception:
                    time_str = datetime_str

            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, time_item)

            # 시리얼 번호
            serial_item = QTableWidgetItem(record.get('serial_number', ''))
            serial_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row_idx, 1, serial_item)

            # MAC 주소
            mac_address = record.get('mac_address', '')
            mac_item = QTableWidgetItem(mac_address)
            mac_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row_idx, 2, mac_item)

            # 상태
            status = record.get('status', '')
            if status == 'success':
                status_display = "성공"
                status_color = colors.SUCCESS
            elif status == 'failed':
                status_display = "실패"
                status_color = colors.ERROR
            else:
                status_display = "-"
                status_color = colors.GRAY_500

            status_item = QTableWidgetItem(status_display)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QBrush(QColor(status_color)))

            # 상태 폰트 굵게
            font = QFont()
            font.setBold(True)
            status_item.setFont(font)

            self.table.setItem(row_idx, 3, status_item)

    def clear(self):
        """테이블 초기화"""
        self._history_data = []
        self.table.setRowCount(0)
