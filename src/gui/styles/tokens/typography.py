"""타이포그래피 토큰 정의"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyTokens:
    """폰트 토큰"""

    # Font Family
    FAMILY: str = "Segoe UI, Arial"
    FAMILY_MONO: str = "Consolas, Monaco"

    # Font Size (px)
    H1: int = 32
    H2: int = 24
    H3: int = 18
    BODY: int = 14
    CAPTION: int = 12
    MONOSPACE: int = 13

    # Font Weight
    REGULAR: int = 400
    MEDIUM: int = 500
    SEMIBOLD: int = 600
    BOLD: int = 700

    def to_variable_map(self) -> dict:
        """QSS 변수 맵 생성"""
        return {
            '@font-family': self.FAMILY,
            '@font-mono': self.FAMILY_MONO,
            '@font-h1': f'{self.H1}px',
            '@font-h2': f'{self.H2}px',
            '@font-h3': f'{self.H3}px',
            '@font-body': f'{self.BODY}px',
            '@font-caption': f'{self.CAPTION}px',
            '@font-mono-size': f'{self.MONOSPACE}px',
            '@font-regular': str(self.REGULAR),
            '@font-medium': str(self.MEDIUM),
            '@font-semibold': str(self.SEMIBOLD),
            '@font-bold': str(self.BOLD),
        }
