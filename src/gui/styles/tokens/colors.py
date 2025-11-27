"""색상 토큰 정의 - Light/Dark 테마"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
    """색상 토큰 - Light 테마 (GitHub Style)"""

    # Primary (액센트)
    PRIMARY: str = "#0969DA"
    PRIMARY_DARK: str = "#0550AE"
    PRIMARY_LIGHT: str = "#DDF4FF"

    # Grayscale
    WHITE: str = "#FFFFFF"
    GRAY_50: str = "#F6F8FA"
    GRAY_100: str = "#EAEEF2"
    GRAY_200: str = "#D0D7DE"
    GRAY_300: str = "#AFB8C1"
    GRAY_400: str = "#8C959F"
    GRAY_500: str = "#6E7781"
    GRAY_600: str = "#57606A"
    GRAY_700: str = "#424A53"
    GRAY_800: str = "#32383F"
    GRAY_900: str = "#1F2328"

    # Semantic
    SUCCESS: str = "#1A7F37"
    SUCCESS_LIGHT: str = "#DAFBE1"
    ERROR: str = "#CF222E"
    ERROR_LIGHT: str = "#FFEBE9"
    WARNING: str = "#9A6700"
    WARNING_LIGHT: str = "#FFF8C5"

    def to_variable_map(self) -> dict:
        """QSS 변수 맵 생성"""
        return {
            '@primary': self.PRIMARY,
            '@primary-dark': self.PRIMARY_DARK,
            '@primary-light': self.PRIMARY_LIGHT,
            '@white': self.WHITE,
            '@gray-50': self.GRAY_50,
            '@gray-100': self.GRAY_100,
            '@gray-200': self.GRAY_200,
            '@gray-300': self.GRAY_300,
            '@gray-400': self.GRAY_400,
            '@gray-500': self.GRAY_500,
            '@gray-600': self.GRAY_600,
            '@gray-700': self.GRAY_700,
            '@gray-800': self.GRAY_800,
            '@gray-900': self.GRAY_900,
            '@success': self.SUCCESS,
            '@success-light': self.SUCCESS_LIGHT,
            '@error': self.ERROR,
            '@error-light': self.ERROR_LIGHT,
            '@warning': self.WARNING,
            '@warning-light': self.WARNING_LIGHT,
        }


@dataclass(frozen=True)
class DarkColorTokens(ColorTokens):
    """색상 토큰 - Dark 테마 (GitHub Dark)"""

    # Primary (밝게 조정)
    PRIMARY: str = "#58A6FF"
    PRIMARY_DARK: str = "#388BFD"
    PRIMARY_LIGHT: str = "#0D1117"

    # Grayscale (반전)
    WHITE: str = "#0D1117"
    GRAY_50: str = "#010409"
    GRAY_100: str = "#161B22"
    GRAY_200: str = "#21262D"
    GRAY_300: str = "#30363D"
    GRAY_400: str = "#484F58"
    GRAY_500: str = "#6E7681"
    GRAY_600: str = "#8B949E"
    GRAY_700: str = "#B1BAC4"
    GRAY_800: str = "#C9D1D9"
    GRAY_900: str = "#F0F6FC"

    # Semantic (어두운 배경용)
    SUCCESS: str = "#3FB950"
    SUCCESS_LIGHT: str = "#238636"
    ERROR: str = "#F85149"
    ERROR_LIGHT: str = "#DA3633"
    WARNING: str = "#D29922"
    WARNING_LIGHT: str = "#9E6A03"
