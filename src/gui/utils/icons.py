"""SVG 아이콘 시스템

간단한 SVG 아이콘을 생성하여 QIcon으로 반환하는 유틸리티
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize


class IconProvider:
    """SVG 아이콘 제공자"""

    @staticmethod
    def _create_icon_from_svg(svg_data: str, size: int = 24, color: str = "#374151") -> QIcon:
        """SVG 데이터에서 QIcon 생성

        Args:
            svg_data: SVG XML 문자열
            size: 아이콘 크기 (픽셀)
            color: 아이콘 색상 (hex)

        Returns:
            QIcon 객체
        """
        # SVG 데이터를 색상으로 치환
        svg_data = svg_data.replace("currentColor", color)

        # SVG 렌더러 생성
        svg_bytes = QByteArray(svg_data.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)

        # Pixmap 생성 및 렌더링
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(QColor(0, 0, 0, 0))  # 투명 배경

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def document_icon(size: int = 24, color: str = "#374151") -> QIcon:
        """문서 아이콘 (기본 정보용)

        Args:
            size: 아이콘 크기
            color: 아이콘 색상

        Returns:
            QIcon 객체
        """
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 18H17V16H7V18ZM7 14H17V12H7V14ZM7 10H11V8H7V10ZM14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                  fill="currentColor"/>
        </svg>'''
        return IconProvider._create_icon_from_svg(svg, size, color)

    @staticmethod
    def settings_icon(size: int = 24, color: str = "#374151") -> QIcon:
        """설정(톱니바퀴) 아이콘 (사양 정보용)

        Args:
            size: 아이콘 크기
            color: 아이콘 색상

        Returns:
            QIcon 객체
        """
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.14 12.94C19.18 12.64 19.2 12.33 19.2 12C19.2 11.68 19.18 11.36 19.13 11.06L21.16 9.48C21.34 9.34 21.39 9.07 21.28 8.87L19.36 5.55C19.24 5.33 18.99 5.26 18.77 5.33L16.38 6.29C15.88 5.91 15.35 5.59 14.76 5.35L14.4 2.81C14.36 2.57 14.16 2.4 13.92 2.4H10.08C9.84 2.4 9.65 2.57 9.61 2.81L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33C5.02 5.25 4.77 5.33 4.65 5.55L2.74 8.87C2.62 9.08 2.66 9.34 2.86 9.48L4.89 11.06C4.84 11.36 4.8 11.69 4.8 12C4.8 12.31 4.82 12.64 4.87 12.94L2.84 14.52C2.66 14.66 2.61 14.93 2.72 15.13L4.64 18.45C4.76 18.67 5.01 18.74 5.23 18.67L7.62 17.71C8.12 18.09 8.65 18.41 9.24 18.65L9.6 21.19C9.65 21.43 9.84 21.6 10.08 21.6H13.92C14.16 21.6 14.36 21.43 14.39 21.19L14.75 18.65C15.34 18.41 15.88 18.09 16.37 17.71L18.76 18.67C18.98 18.75 19.23 18.67 19.35 18.45L21.27 15.13C21.39 14.91 21.34 14.66 21.15 14.52L19.14 12.94ZM12 15.6C10.02 15.6 8.4 13.98 8.4 12C8.4 10.02 10.02 8.4 12 8.4C13.98 8.4 15.6 10.02 15.6 12C15.6 13.98 13.98 15.6 12 15.6Z"
                  fill="currentColor"/>
        </svg>'''
        return IconProvider._create_icon_from_svg(svg, size, color)

    @staticmethod
    def factory_icon(size: int = 24, color: str = "#374151") -> QIcon:
        """공장 아이콘 (생산 정보용)

        Args:
            size: 아이콘 크기
            color: 아이콘 색상

        Returns:
            QIcon 객체
        """
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 22H2V10L7 12.5V10L12 12.5V5L17 9V2H19V9L22 11V22ZM20 20V12.5L17 11V13.5L12 11V13.5L7 11V14L4 12.5V20H20ZM11 18H9V15H11V18ZM15 18H13V15H15V18Z"
                  fill="currentColor"/>
        </svg>'''
        return IconProvider._create_icon_from_svg(svg, size, color)

    @staticmethod
    def get_icon(icon_type: str, size: int = 20, color: str = "#374151") -> QIcon:
        """아이콘 타입에 따라 아이콘 반환

        Args:
            icon_type: "document", "settings", "factory" 중 하나
            size: 아이콘 크기
            color: 아이콘 색상

        Returns:
            QIcon 객체
        """
        icons = {
            "document": IconProvider.document_icon,
            "settings": IconProvider.settings_icon,
            "factory": IconProvider.factory_icon,
        }

        icon_func = icons.get(icon_type.lower())
        if icon_func:
            return icon_func(size, color)
        else:
            # 기본값: 문서 아이콘
            return IconProvider.document_icon(size, color)
