"""동적 스타일 헬퍼

Qt Property를 활용하여 런타임에 스타일을 동적으로 변경합니다.
QSS에서 [property="value"] 셀렉터로 매칭됩니다.

사용 예:
    # Python
    DynamicStyle.set_status(label, "connected")

    # QSS
    QLabel[data-status="connected"] { color: @success; }
"""

from PyQt6.QtWidgets import QWidget


class DynamicStyle:
    """동적 스타일 적용 헬퍼 클래스"""

    @staticmethod
    def set_status(widget: QWidget, status: str):
        """상태 기반 스타일 적용

        상태: connected, disconnected, checking, pending, success, error 등

        Args:
            widget: 대상 위젯
            status: 상태 문자열
        """
        widget.setProperty('data-status', status)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @staticmethod
    def set_variant(widget: QWidget, variant: str):
        """변형 스타일 적용

        변형: primary, secondary, success, error, warning 등

        Args:
            widget: 대상 위젯
            variant: 변형 문자열
        """
        widget.setProperty('data-variant', variant)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @staticmethod
    def set_state(widget: QWidget, state: str, value: bool):
        """상태 플래그 설정

        상태: active, disabled, selected, hover 등

        Args:
            widget: 대상 위젯
            state: 상태 이름
            value: True/False
        """
        widget.setProperty(f'data-{state}', 'true' if value else 'false')
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @staticmethod
    def set_active(widget: QWidget, active: bool):
        """활성 상태 설정 (사이드바 메뉴 등)

        Args:
            widget: 대상 위젯
            active: 활성 여부
        """
        DynamicStyle.set_state(widget, 'active', active)

    @staticmethod
    def set_color_type(widget: QWidget, color_type: str):
        """색상 타입 설정

        타입: success, error, warning, primary, muted 등

        Args:
            widget: 대상 위젯
            color_type: 색상 타입 문자열
        """
        widget.setProperty('data-color', color_type)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @staticmethod
    def clear(widget: QWidget, *properties: str):
        """동적 속성 제거

        Args:
            widget: 대상 위젯
            properties: 제거할 속성 이름들 (예: 'data-status', 'data-variant')
        """
        for prop in properties:
            widget.setProperty(prop, None)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()


class StyledWidgetMixin:
    """스타일 믹스인 - 위젯 클래스에 추가하여 동적 스타일 메서드 제공

    사용 예:
        class MyWidget(QWidget, StyledWidgetMixin):
            def update_status(self, status):
                self.set_style_status(status)
    """

    def set_style_status(self, status: str):
        """상태 스타일 적용"""
        DynamicStyle.set_status(self, status)

    def set_style_variant(self, variant: str):
        """변형 스타일 적용"""
        DynamicStyle.set_variant(self, variant)

    def set_style_state(self, state: str, value: bool):
        """상태 플래그 설정"""
        DynamicStyle.set_state(self, state, value)

    def set_style_active(self, active: bool):
        """활성 상태 설정"""
        DynamicStyle.set_active(self, active)

    def set_style_color(self, color_type: str):
        """색상 타입 설정"""
        DynamicStyle.set_color_type(self, color_type)

    def clear_style(self, *properties: str):
        """동적 속성 제거"""
        DynamicStyle.clear(self, *properties)
