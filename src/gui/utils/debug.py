"""GUI 디버깅 유틸리티

체크리스트 섹션 5 (디버깅 및 시각화) 준수:
- 위젯 크기 정보 출력
- 레이아웃 경계 시각화
- 개발 모드 배경색 적용
"""
from PyQt6.QtWidgets import QWidget

class DebugUtils:
    """GUI 디버깅 헬퍼"""

    @staticmethod
    def print_widget_info(widget: QWidget, name: str = "Widget"):
        """위젯 크기 및 상태 정보 출력

        Args:
            widget: 정보를 출력할 위젯
            name: 위젯 이름 (디버그용)
        """
        print(f"\n{'='*60}")
        print(f"📊 {name} 정보:")
        print(f"{'='*60}")
        print(f"  크기 (size):         {widget.size().width()}x{widget.size().height()}")
        print(f"  최소 크기 (minimum): {widget.minimumSize().width()}x{widget.minimumSize().height()}")
        print(f"  최대 크기 (maximum): {widget.maximumSize().width()}x{widget.maximumSize().height()}")
        print(f"  표시 여부 (visible): {widget.isVisible()}")
        print(f"  활성화 (enabled):    {widget.isEnabled()}")
        print(f"  ObjectName:          {widget.objectName()}")
        print(f"{'='*60}\n")

    @staticmethod
    def print_layout_tree(widget: QWidget, indent: int = 0):
        """위젯 트리 구조 출력

        Args:
            widget: 루트 위젯
            indent: 들여쓰기 레벨
        """
        prefix = "  " * indent
        widget_type = widget.__class__.__name__
        object_name = widget.objectName() or "(no name)"
        size = f"{widget.size().width()}x{widget.size().height()}"

        print(f"{prefix}├─ {widget_type} [{object_name}] - {size}")

        # 자식 위젯 순회
        for child in widget.children():
            if isinstance(child, QWidget):
                DebugUtils.print_layout_tree(child, indent + 1)

    @staticmethod
    def apply_debug_borders(widget: QWidget, colors: dict = None):
        """디버그용 배경색 및 테두리 적용

        Args:
            widget: 타겟 위젯
            colors: 색상 딕셔너리 (기본값: 랜덤 파스텔 색상)
        """
        if colors is None:
            colors = {
                "Card": "background-color: #FFF5F5; border: 2px solid #FF0000;",
                "Section": "background-color: #F0F9FF; border: 1px dashed #0000FF;",
                "FormRow": "background-color: #F0FFF4; border: 1px dotted #00FF00;",
                "SelectRow": "background-color: #FFFBEB; border: 1px dotted #FFAA00;",
                "InputRow": "background-color: #FFF7ED; border: 1px dotted #FF6600;",
                "DisplayRow": "background-color: #F5F3FF; border: 1px dotted #AA00FF;",
                "ButtonRow": "background-color: #ECFDF5; border: 1px dotted #00AA00;",
            }

        def apply_recursive(w: QWidget):
            class_name = w.__class__.__name__
            if class_name in colors:
                current_style = w.styleSheet()
                w.setStyleSheet(f"{current_style}\n{class_name} {{ {colors[class_name]} }}")

            for child in w.children():
                if isinstance(child, QWidget):
                    apply_recursive(child)

        apply_recursive(widget)

    @staticmethod
    def validate_layout(widget: QWidget) -> list:
        """레이아웃 검증 - 문제 있는 위젯 찾기

        Args:
            widget: 검증할 루트 위젯

        Returns:
            문제 목록 (빈 리스트면 정상)
        """
        issues = []

        def check_recursive(w: QWidget, path: str = ""):
            current_path = f"{path}/{w.objectName() or w.__class__.__name__}"

            # 1. 크기가 0인 위젯 체크
            if w.isVisible() and (w.size().width() == 0 or w.size().height() == 0):
                issues.append(f"❌ 크기 0: {current_path} - {w.size().width()}x{w.size().height()}")

            # 2. objectName 없는 주요 위젯 체크
            if not w.objectName() and w.__class__.__name__ in ["Card", "Section", "FormRow", "SelectRow"]:
                issues.append(f"⚠️  objectName 없음: {current_path}")

            # 3. 레이아웃 없는 컨테이너 체크
            if w.children() and not w.layout():
                issues.append(f"⚠️  레이아웃 없음: {current_path}")

            # 자식 검증
            for child in w.children():
                if isinstance(child, QWidget):
                    check_recursive(child, current_path)

        check_recursive(widget)
        return issues

def enable_debug_mode(main_window, print_tree: bool = True, show_borders: bool = True):
    """디버그 모드 활성화

    Args:
        main_window: MainWindow 인스턴스
        print_tree: 위젯 트리 출력 여부
        show_borders: 배경색/테두리 표시 여부
    """
    print("\n" + "="*60)
    print("🐛 DEBUG MODE ENABLED")
    print("="*60)

    if print_tree:
        print("\n📋 위젯 트리 구조:")
        DebugUtils.print_layout_tree(main_window)

    if show_borders:
        print("\n🎨 디버그 테두리 적용 중...")
        DebugUtils.apply_debug_borders(main_window)

    # 레이아웃 검증
    print("\n✅ 레이아웃 검증:")
    issues = DebugUtils.validate_layout(main_window)
    if issues:
        print(f"  발견된 문제: {len(issues)}개")
        for issue in issues:
            print(f"    {issue}")
    else:
        print("  ✅ 문제 없음!")

    print("\n" + "="*60 + "\n")
