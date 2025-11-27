"""검색 패널 컴포넌트 - 하이퍼 미니멀리즘"""
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit
)
from PyQt6.QtCore import pyqtSignal, QDate
from ..core import ComponentBase, Theme


class SearchPanel(ComponentBase):
    """검색 패널

    Signals:
        search_requested: 검색 버튼 클릭 시 필터 딕셔너리 전달
        reset_requested: 초기화 버튼 클릭 시
    """
    search_requested = pyqtSignal(dict)
    reset_requested = pyqtSignal()

    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setObjectName("SearchPanel")  # QSS 셀렉터용

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ========== 필터 입력 행 ==========
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        # 날짜 범위
        date_label = QLabel("기간")
        date_label.setProperty("data-role", "filter-label")  # QSS 셀렉터용
        filter_layout.addWidget(date_label)

        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setMinimumWidth(145)
        self.date_from.setFixedHeight(36)
        self.date_from.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        filter_layout.addWidget(self.date_from)

        dash = QLabel("~")
        dash.setProperty("data-role", "separator")  # QSS 셀렉터용
        filter_layout.addWidget(dash)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setMinimumWidth(145)
        self.date_to.setFixedHeight(36)
        self.date_to.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        filter_layout.addWidget(self.date_to)

        filter_layout.addSpacing(16)

        # 시리얼 번호 검색
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("시리얼 번호 검색...")
        self.serial_input.setFixedWidth(135)
        self.serial_input.setFixedHeight(36)
        filter_layout.addWidget(self.serial_input)

        # MAC 주소 검색
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("MAC 주소 검색...")
        self.mac_input.setFixedWidth(135)
        self.mac_input.setFixedHeight(36)
        filter_layout.addWidget(self.mac_input)

        filter_layout.addStretch()

        # 버튼 영역
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # 초기화 버튼
        reset_btn = QPushButton("초기화")
        reset_btn.setFixedHeight(36)
        reset_btn.setFixedWidth(80)
        reset_btn.setProperty("data-role", "search-secondary")  # QSS 셀렉터용
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        # 검색 버튼
        search_btn = QPushButton("검색")
        search_btn.setFixedHeight(36)
        search_btn.setFixedWidth(80)
        search_btn.setProperty("data-role", "search-primary")  # QSS 셀렉터용
        search_btn.clicked.connect(self._on_search)
        btn_layout.addWidget(search_btn)

        filter_layout.addLayout(btn_layout)

        main_layout.addLayout(filter_layout)

        # ========== 결과 카운트 (나중에 업데이트) ==========
        self.result_label = QLabel("전체 기록")
        self.result_label.setProperty("data-role", "result-count")  # QSS 셀렉터용
        main_layout.addWidget(self.result_label)

    def _on_search(self):
        """검색 버튼 클릭"""
        filters = self.get_filters()
        self.search_requested.emit(filters)

    def _on_reset(self):
        """초기화 버튼 클릭"""
        # 필터 초기화
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.serial_input.clear()
        self.mac_input.clear()

        self.reset_requested.emit()

    def get_filters(self):
        """현재 필터 값 반환

        Returns:
            dict: {
                'date_from': str or None,
                'date_to': str or None,
                'serial_number': str or None,
                'mac_address': str or None
            }
        """
        return {
            'date_from': self.date_from.date().toString("yyyy-MM-dd"),
            'date_to': self.date_to.date().toString("yyyy-MM-dd"),
            'serial_number': self.serial_input.text().strip() or None,
            'mac_address': self.mac_input.text().strip() or None
        }

    def set_result_count(self, count):
        """검색 결과 개수 표시

        Args:
            count: 결과 개수
        """
        self.result_label.setText(f"검색 결과: {count}건")

    def reset_result_count(self):
        """결과 개수 표시 초기화"""
        self.result_label.setText("전체 기록")
