"""컴포넌트 베이스 클래스"""
from PyQt6.QtWidgets import QWidget, QSizePolicy

class ComponentBase(QWidget):
    def __init__(self, parent=None, fixed_height=None, min_height=None, fixed_width=None, min_width=None):
        super().__init__(parent)
        if fixed_height:
            self.setFixedHeight(fixed_height)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif min_height:
            self.setMinimumHeight(min_height)

        if fixed_width:
            self.setFixedWidth(fixed_width)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        elif min_width:
            self.setMinimumWidth(min_width)

class RowBase(ComponentBase):
    def __init__(self, parent=None):
        from .layout_system import LayoutSystem
        super().__init__(parent, fixed_height=LayoutSystem.ROW_HEIGHT)
