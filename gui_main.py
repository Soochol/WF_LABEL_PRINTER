"""
GUI Application Entry Point
Zebra Label Printer - PyQt6 GUI
"""

import sys
import io
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from src.gui import MainWindow


def main():
    """GUI 애플리케이션 실행"""

    # Windows에서 UTF-8 인코딩 강제 설정
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except (AttributeError, io.UnsupportedOperation):
            # 이미 wrapper이거나 buffer가 없는 경우 무시
            pass

    # High DPI 지원
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # QApplication 생성
    app = QApplication(sys.argv)
    app.setApplicationName("Zebra Label Printer")
    app.setOrganizationName("WF")

    try:
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
    except Exception as e:
        import traceback
        error_msg = f"오류 발생:\n{str(e)}\n\n{traceback.format_exc()}"

        # 오류를 파일로 저장
        try:
            import os
            from pathlib import Path
            # AppData에 오류 로그 저장
            if getattr(sys, 'frozen', False):
                log_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "WF_Label_Printer" / "logs"
            else:
                log_dir = Path("logs")
            log_dir.mkdir(parents=True, exist_ok=True)

            with open(log_dir / "crash_log.txt", "w", encoding="utf-8") as f:
                f.write(error_msg)
        except:
            pass

        # 메시지 박스로 오류 표시
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("오류")
        msg.setText("프로그램 실행 중 오류가 발생했습니다.")
        msg.setDetailedText(error_msg)
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()
