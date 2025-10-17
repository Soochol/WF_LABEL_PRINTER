"""
GUI Application Entry Point
Zebra Label Printer - PyQt6 GUI
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from src.gui import MainWindow


def main():
    """GUI 애플리케이션 실행"""

    # High DPI 지원
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # QApplication 생성
    app = QApplication(sys.argv)
    app.setApplicationName("Zebra Label Printer")
    app.setOrganizationName("WF")

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 디버그 모드: 1초 후 geometry 정보 출력
    if "--debug-geometry" in sys.argv:
        def print_debug():
            window.debug_print_geometry()
        QTimer.singleShot(1000, print_debug)

    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
