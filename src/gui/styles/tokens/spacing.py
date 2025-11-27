"""간격 토큰 정의"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacingTokens:
    """간격 및 레이아웃 토큰"""

    # 고정 높이
    ROW_HEIGHT: int = 60
    INPUT_HEIGHT: int = 48
    BUTTON_HEIGHT: int = 44
    LABEL_HEIGHT: int = 24
    HEADER_HEIGHT: int = 56

    # 고정 너비
    SIDEBAR_WIDTH: int = 220
    LABEL_WIDTH: int = 140
    BUTTON_MIN_WIDTH: int = 100
    BUTTON_PRIMARY_WIDTH: int = 140

    # 간격
    SECTION: int = 32
    CARD: int = 24
    ROW: int = 16
    ITEM: int = 12
    BUTTON: int = 8

    # 여백
    PADDING_CARD: int = 24
    PADDING_SECTION: int = 16
    MARGIN_PAGE: int = 24

    # 테두리
    BORDER_RADIUS: int = 8
    BORDER_RADIUS_SM: int = 6
    BORDER_RADIUS_LG: int = 12
    BORDER_WIDTH: int = 1

    def to_variable_map(self) -> dict:
        """QSS 변수 맵 생성"""
        return {
            '@row-height': f'{self.ROW_HEIGHT}px',
            '@input-height': f'{self.INPUT_HEIGHT}px',
            '@button-height': f'{self.BUTTON_HEIGHT}px',
            '@sidebar-width': f'{self.SIDEBAR_WIDTH}px',
            '@spacing-section': f'{self.SECTION}px',
            '@spacing-card': f'{self.CARD}px',
            '@spacing-row': f'{self.ROW}px',
            '@spacing-item': f'{self.ITEM}px',
            '@spacing-button': f'{self.BUTTON}px',
            '@padding-card': f'{self.PADDING_CARD}px',
            '@padding-section': f'{self.PADDING_SECTION}px',
            '@margin-page': f'{self.MARGIN_PAGE}px',
            '@radius': f'{self.BORDER_RADIUS}px',
            '@radius-sm': f'{self.BORDER_RADIUS_SM}px',
            '@radius-lg': f'{self.BORDER_RADIUS_LG}px',
            '@border-width': f'{self.BORDER_WIDTH}px',
        }
