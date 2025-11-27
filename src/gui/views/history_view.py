"""이력 화면 - 반응형 디자인"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QScrollArea, QWidget,
    QFrame, QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont
from ..core import ComponentBase, Theme
from ..components.search_panel import SearchPanel
from ..styles import get_theme_manager
from ..styles.theme_manager import ThemeMode


class HistoryView(ComponentBase):
    """이력 뷰"""

    # Signals
    search_requested = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    delete_requested = pyqtSignal(int)

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("HistoryView")

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # 스크롤 컨텐츠
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # ========== 헤더 ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # 타이틀
        title = QLabel("Print History")
        title.setProperty("data-role", "view-title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # 삭제 버튼
        self.delete_btn = QPushButton("삭제")
        self.delete_btn.setProperty("data-role", "view-danger")
        self.delete_btn.setMinimumHeight(36)
        self.delete_btn.setMinimumWidth(80)
        self.delete_btn.setMaximumWidth(120)
        self.delete_btn.clicked.connect(self._on_delete)
        header_layout.addWidget(self.delete_btn)

        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setProperty("data-role", "view-secondary")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setMinimumWidth(80)
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.clicked.connect(self._on_refresh)
        header_layout.addWidget(self.refresh_btn)

        content_layout.addLayout(header_layout)

        # ========== 검색 패널 ==========
        self.search_panel = SearchPanel(self.theme)
        self.search_panel.search_requested.connect(self._on_search)
        self.search_panel.reset_requested.connect(self._on_reset)
        self.search_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        content_layout.addWidget(self.search_panel)

        # ========== 테이블 ==========
        self.table = QTableWidget()
        self.table.setObjectName("HistoryTable")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "시리얼 번호", "MAC 주소", "출력 일시", "PRN 템플릿"
        ])

        # 테이블 설정
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(True)

        # 열 너비 설정 (반응형)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 160)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # 행 높이
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 테이블 크기 정책
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.table.setMinimumHeight(300)

        content_layout.addWidget(self.table, 1)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 스타일 적용
        self._apply_style()

        # 테마 변경 연결
        theme_mgr = get_theme_manager()
        theme_mgr.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _):
        self._apply_style()

    def _apply_style(self):
        theme_mgr = get_theme_manager()
        colors = theme_mgr.colors
        is_dark = theme_mgr.mode == ThemeMode.DARK

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
        """)

        # 스크롤바 스타일
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
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
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 8px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {colors.GRAY_400};
                border-radius: 4px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {colors.GRAY_500};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
        """)

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

        # 행에서 record_id 가져오기
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
            self.delete_requested.emit(record_id)

    def set_history(self, history_list, update_count=True):
        """이력 데이터 설정"""
        self.table.setRowCount(0)

        # 검색 결과 개수 업데이트
        if update_count:
            self.search_panel.set_result_count(len(history_list))

        for record in history_list:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 시리얼 번호 (record_id를 UserRole에 저장)
            serial_item = QTableWidgetItem(record.get('serial_number', ''))
            serial_item.setData(Qt.ItemDataRole.UserRole, record.get('id'))
            self.table.setItem(row_idx, 0, serial_item)

            # MAC 주소
            self.table.setItem(
                row_idx, 1,
                QTableWidgetItem(record.get('mac_address', ''))
            )

            # 출력 일시
            self.table.setItem(
                row_idx, 2,
                QTableWidgetItem(record.get('print_datetime', ''))
            )

            # PRN 템플릿
            self.table.setItem(
                row_idx, 3,
                QTableWidgetItem(record.get('prn_template', ''))
            )

    def add_record(self, record):
        """단일 레코드 추가"""
        self.table.insertRow(0)

        serial_item = QTableWidgetItem(record.get('serial_number', ''))
        serial_item.setData(Qt.ItemDataRole.UserRole, record.get('id'))
        self.table.setItem(0, 0, serial_item)
        self.table.setItem(0, 1, QTableWidgetItem(record.get('mac_address', '')))
        self.table.setItem(0, 2, QTableWidgetItem(record.get('print_datetime', '')))
        self.table.setItem(0, 3, QTableWidgetItem(record.get('prn_template', '')))
