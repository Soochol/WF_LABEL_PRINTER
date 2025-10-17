"""SVG 아이콘 유틸리티"""
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize

class SvgIcon:
    """SVG 아이콘 관리 클래스"""

    # SVG 아이콘 정의 (Material Design Icons 스타일)
    ICONS = {
        "home": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
        </svg>
        """,

        "print": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
        </svg>
        """,

        "config": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
        </svg>
        """,

        "settings": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/>
        </svg>
        """,

        "history": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
        </svg>
        """,
    }

    @staticmethod
    def create_icon(icon_name: str, color: str = "#FFFFFF", size: int = 24) -> QIcon:
        """SVG 문자열로부터 QIcon 생성

        Args:
            icon_name: 아이콘 이름 ("home", "print", "config", "settings", "history")
            color: 아이콘 색상 (hex)
            size: 아이콘 크기 (픽셀)

        Returns:
            QIcon 객체
        """
        if icon_name not in SvgIcon.ICONS:
            # 기본 아이콘 반환
            return QIcon()

        # SVG 문자열에서 색상 적용
        svg_string = SvgIcon.ICONS[icon_name].replace('fill="currentColor"', f'fill="{color}"')

        # SVG 렌더러 생성
        renderer = QSvgRenderer(svg_string.encode('utf-8'))

        # 픽스맵 생성
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        # SVG를 픽스맵에 렌더링
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def create_pixmap(icon_name: str, color: str = "#FFFFFF", size: int = 24) -> QPixmap:
        """SVG 문자열로부터 QPixmap 생성

        Args:
            icon_name: 아이콘 이름
            color: 아이콘 색상 (hex)
            size: 아이콘 크기 (픽셀)

        Returns:
            QPixmap 객체
        """
        if icon_name not in SvgIcon.ICONS:
            return QPixmap()

        svg_string = SvgIcon.ICONS[icon_name].replace('fill="currentColor"', f'fill="{color}"')
        renderer = QSvgRenderer(svg_string.encode('utf-8'))

        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap