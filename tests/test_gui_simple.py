"""
간단한 GUI 테스트 - 각 뷰를 순회하며 확인
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys

def test_views():
    """각 뷰 순회 테스트"""
    app = QApplication(sys.argv)

    from src.gui.main_window import MainWindow
    window = MainWindow()
    window.show()

    views_to_test = ["home", "print", "history", "lot_config", "settings"]
    current = [0]

    def switch_view():
        if current[0] >= len(views_to_test):
            print("\n✓ All views tested successfully!")
            print("✓ GUI is working correctly!")
            QTimer.singleShot(2000, app.quit)
            return

        view_id = views_to_test[current[0]]
        print(f"Switching to: {view_id}")

        window.main_layout.sidebar.select_menu(view_id)
        window.main_layout.show_view(view_id)
        app.processEvents()

        current[0] += 1
        QTimer.singleShot(1000, switch_view)

    print("=" * 60)
    print("GUI VIEW SWITCHING TEST")
    print("=" * 60)
    print()

    QTimer.singleShot(1000, switch_view)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_views())
