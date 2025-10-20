"""이력 화면 - 하이퍼 미니멀리즘 디자인"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
from ..core import ComponentBase, Theme
from ..components.search_panel import SearchPanel

class HistoryView(ComponentBase):
    """이력 뷰"""

    # Signals
    search_requested = pyqtSignal(dict)  # 검색 요청
    refresh_requested = pyqtSignal()     # 새로고침 요청
    delete_requested = pyqtSignal(int)   # 삭제 요청 (record_id)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()

        # 배경색
        self.setStyleSheet(f"""
            HistoryView {{
                background-color: {self.theme.colors.GRAY_50};
            }}
        """)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # ========== 헤더 ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # 타이틀
        title = QLabel("Print History")
        title.setStyleSheet(f"""
            font-size: {self.theme.fonts.H1}px;
            font-weight: {self.theme.fonts.BOLD};
            color: {self.theme.colors.GRAY_900};
            background: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # 삭제 버튼
        delete_btn = QPushButton("삭제")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors.WHITE};
                color: {self.theme.colors.ERROR};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: {self.theme.fonts.MEDIUM};
                font-size: {self.theme.fonts.BODY}px;
            }}
            QPushButton:hover {{
                background-color: #FEE;
                border-color: {self.theme.colors.ERROR};
            }}
        """)
        delete_btn.setFixedHeight(40)
        delete_btn.setFixedWidth(100)
        delete_btn.clicked.connect(self._on_delete)
        header_layout.addWidget(delete_btn)

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
        refresh_btn.clicked.connect(self._on_refresh)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # ========== 검색 패널 ==========
        self.search_panel = SearchPanel(self.theme)
        self.search_panel.search_requested.connect(self._on_search)
        self.search_panel.reset_requested.connect(self._on_reset)
        main_layout.addWidget(self.search_panel)

        # ========== 테이블 ==========
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "시리얼 번호", "MAC 주소", "출력 일시", "PRN 템플릿"
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
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 열 너비 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 시리얼 번호
        header.resizeSection(0, 220)  # 20자 시리얼 번호
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # MAC 주소
        header.resizeSection(1, 180)  # 17자 MAC 주소
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 출력 일시
        header.resizeSection(2, 160)  # 날짜+시간
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # PRN 템플릿

        main_layout.addWidget(self.table)

    def _on_refresh(self):
        """새로고침"""
        self.refresh_requested.emit()

    def _on_search(self, filters):
        """검색 요청"""
        self.search_requested.emit(filters)

    def _on_reset(self):
        """초기화 - 전체 기록 표시"""
        self.refresh_requested.emit()

    def _on_delete(self):
        """선택한 이력 삭제"""
        from PyQt6.QtWidgets import QMessageBox

        # 선택된 행 가져오기
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "삭제", "삭제할 항목을 선택해주세요.")
            return

        row = selected_rows[0].row()

        # 행에서 record_id 가져오기 (첫 번째 컬럼의 UserRole 데이터로 저장됨)
        item = self.table.item(row, 0)
        if not item:
            return

        record_id = item.data(Qt.ItemDataRole.UserRole)
        if not record_id:
            return

        # 삭제 확인
        serial_number = self.table.item(row, 0).text()
        mac_address = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"다음 항목을 삭제하시겠습니까?\n\n"
            f"시리얼 번호: {serial_number}\n"
            f"MAC 주소: {mac_address}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 삭제 요청 시그널 발생
            self.delete_requested.emit(record_id)


    def set_history(self, history_list, update_count=True):
        """이력 데이터 설정

        Args:
            history_list: 이력 레코드 리스트
            update_count: 검색 결과 개수 업데이트 여부
        """
        self.table.setRowCount(0)

        # 검색 결과 개수 업데이트
        if update_count:
            self.search_panel.set_result_count(len(history_list))

        for record in history_list:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 시리얼 번호 (record_id를 UserRole에 저장)
            serial_item = QTableWidgetItem(record.get('serial_number', ''))
            serial_item.setData(Qt.ItemDataRole.UserRole, record.get('id'))  # ID 저장
            self.table.setItem(row_idx, 0, serial_item)

            # MAC 주소
            self.table.setItem(row_idx, 1, QTableWidgetItem(record.get('mac_address', '')))

            # 출력 일시
            self.table.setItem(row_idx, 2, QTableWidgetItem(record.get('print_datetime', '')))

            # PRN 템플릿
            self.table.setItem(row_idx, 3, QTableWidgetItem(record.get('prn_template', '')))

    def add_record(self, record):
        """단일 레코드 추가"""
        row_idx = self.table.rowCount()
        self.table.insertRow(0)  # 최상단에 추가

        self.table.setItem(0, 0, QTableWidgetItem(record.get('serial_number', '')))
        self.table.setItem(0, 1, QTableWidgetItem(record.get('mac_address', '')))
        self.table.setItem(0, 2, QTableWidgetItem(record.get('print_datetime', '')))
        self.table.setItem(0, 3, QTableWidgetItem(record.get('prn_template', '')))
