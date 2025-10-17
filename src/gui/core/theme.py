"""테마 시스템"""


class Colors:
    """색상 팔레트 - 미니멀리즘 (최소 색상만 사용)"""

    # Primary (액센트만 사용)
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1E40AF"
    PRIMARY_LIGHT = "#DBEAFE"

    # Grayscale (주요 색상)
    WHITE = "#FFFFFF"
    GRAY_50 = "#F9FAFB"
    GRAY_100 = "#F3F4F6"
    GRAY_200 = "#E5E7EB"
    GRAY_300 = "#D1D5DB"
    GRAY_400 = "#9CA3AF"
    GRAY_500 = "#6B7280"
    GRAY_600 = "#4B5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1F2937"
    GRAY_900 = "#111827"

    # Semantic (최소 사용)
    SUCCESS = "#10B981"
    ERROR = "#EF4444"


class Fonts:
    """폰트 설정"""
    FAMILY = "Segoe UI, Arial"
    FAMILY_MONO = "Consolas, Monaco"
    H1 = 32
    H2 = 24
    H3 = 18
    BODY = 14
    CAPTION = 12
    MONOSPACE = 13
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700


class Theme:
    """테마 시스템

    DEBUG 모드: 환경변수 GUI_DEBUG=1 설정 시 디버그 모드 활성화
    """
    DEBUG = False  # 개발 중 True로 설정하여 디버그 모드 활성화

    def __init__(self):
        self.colors = Colors()
        self.fonts = Fonts()

    def get_global_stylesheet(self):
        """글로벌 스타일시트 반환"""
        return f"""
            * {{
                font-family: {self.fonts.FAMILY};
                font-size: {self.fonts.BODY}px;
                color: {self.colors.GRAY_900};
            }}
            QWidget {{ background-color: {self.colors.WHITE}; }}
            QLabel {{ background-color: transparent; }}
            QLineEdit, QComboBox {{
                background-color: {self.colors.WHITE};
                border: 1px solid {self.colors.GRAY_300};
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {self.colors.PRIMARY};
                border-width: 2px;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: {self.fonts.MEDIUM};
            }}
            QPushButton[primary="true"] {{
                background-color: {self.colors.PRIMARY};
                color: {self.colors.WHITE};
            }}
            QPushButton[primary="true"]:hover {{
                background-color: {self.colors.PRIMARY_DARK};
            }}
            QPushButton[secondary="true"] {{
                background-color: {self.colors.GRAY_100};
                border: 1px solid {self.colors.GRAY_300};
            }}
            QPushButton[secondary="true"]:hover {{
                background-color: {self.colors.GRAY_200};
            }}
            QScrollArea {{
                border: none;
                background-color: {self.colors.GRAY_50};
            }}
        """
