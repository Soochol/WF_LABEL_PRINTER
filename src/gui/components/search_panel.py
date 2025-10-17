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

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 배경 스타일
        self.setStyleSheet(f"""
            SearchPanel {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_200};
                border-radius: 8px;
            }}
        """)

        # ========== 필터 입력 행 ==========
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        # 날짜 범위
        date_label = QLabel("기간")
        date_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.CAPTION}px;
            font-weight: {self.theme.fonts.SEMIBOLD};
            color: {self.theme.colors.GRAY_700};
        """)
        filter_layout.addWidget(date_label)

        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setMinimumWidth(145)
        self.date_from.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        self._style_date_edit(self.date_from)
        filter_layout.addWidget(self.date_from)

        dash = QLabel("~")
        dash.setStyleSheet(f"color: {self.theme.colors.GRAY_500};")
        filter_layout.addWidget(dash)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setMinimumWidth(145)
        self.date_to.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        self._style_date_edit(self.date_to)
        filter_layout.addWidget(self.date_to)

        filter_layout.addSpacing(16)

        # 시리얼 번호 검색
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("시리얼 번호 검색...")
        self.serial_input.setFixedWidth(135)
        self._style_line_edit(self.serial_input)
        filter_layout.addWidget(self.serial_input)

        # MAC 주소 검색
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("MAC 주소 검색...")
        self.mac_input.setFixedWidth(135)
        self._style_line_edit(self.mac_input)
        filter_layout.addWidget(self.mac_input)

        filter_layout.addStretch()

        # 버튼 영역
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # 초기화 버튼
        reset_btn = QPushButton("초기화")
        reset_btn.setFixedHeight(36)
        reset_btn.setFixedWidth(80)
        reset_btn.clicked.connect(self._on_reset)
        self._style_button(reset_btn, is_primary=False)
        btn_layout.addWidget(reset_btn)

        # 검색 버튼
        search_btn = QPushButton("검색")
        search_btn.setFixedHeight(36)
        search_btn.setFixedWidth(80)
        search_btn.clicked.connect(self._on_search)
        self._style_button(search_btn, is_primary=True)
        btn_layout.addWidget(search_btn)

        filter_layout.addLayout(btn_layout)

        main_layout.addLayout(filter_layout)

        # ========== 결과 카운트 (나중에 업데이트) ==========
        self.result_label = QLabel("전체 기록")
        self.result_label.setStyleSheet(f"""
            font-size: {self.theme.fonts.CAPTION}px;
            color: {self.theme.colors.GRAY_600};
            padding-top: 4px;
        """)
        main_layout.addWidget(self.result_label)

    def _style_date_edit(self, widget):
        """날짜 선택기 스타일"""
        widget.setStyleSheet(f"""
            QDateEdit {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 6px;
                padding: 6px 4px;
                padding-right: 28px;
                font-size: {self.theme.fonts.BODY}px;
                color: {self.theme.colors.GRAY_900};
            }}
            QDateEdit:focus {{
                border-color: {self.theme.colors.PRIMARY};
                outline: none;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 28px;
                border: none;
                background-color: transparent;
            }}
            QDateEdit::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {self.theme.colors.GRAY_600};
                width: 0px;
                height: 0px;
                margin-right: 8px;
            }}
            QDateEdit::down-arrow:hover {{
                border-top-color: {self.theme.colors.GRAY_900};
            }}
        """)
        widget.setFixedHeight(36)

    def _style_line_edit(self, widget):
        """텍스트 입력 스타일"""
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.colors.WHITE};
                border: 1px solid {self.theme.colors.GRAY_300};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: {self.theme.fonts.BODY}px;
                color: {self.theme.colors.GRAY_900};
            }}
            QLineEdit:focus {{
                border-color: {self.theme.colors.PRIMARY};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {self.theme.colors.GRAY_400};
            }}
        """)
        widget.setFixedHeight(36)

    def _style_button(self, widget, is_primary=False):
        """버튼 스타일"""
        if is_primary:
            widget.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme.colors.PRIMARY};
                    color: {self.theme.colors.WHITE};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: {self.theme.fonts.SEMIBOLD};
                    font-size: {self.theme.fonts.BODY}px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.colors.PRIMARY_DARK};
                }}
                QPushButton:pressed {{
                    background-color: {self.theme.colors.PRIMARY_DARK};
                }}
            """)
        else:
            widget.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme.colors.WHITE};
                    color: {self.theme.colors.GRAY_700};
                    border: 1px solid {self.theme.colors.GRAY_300};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: {self.theme.fonts.MEDIUM};
                    font-size: {self.theme.fonts.BODY}px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.colors.GRAY_50};
                    border-color: {self.theme.colors.GRAY_400};
                }}
            """)

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
