"""테마 매니저 - 싱글톤 패턴"""

from enum import Enum
from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from .tokens import ColorTokens, DarkColorTokens, TypographyTokens, SpacingTokens
from .style_loader import StyleLoader
from .style_compiler import StyleCompiler


class ThemeMode(Enum):
    """테마 모드"""
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    """테마 매니저 싱글톤

    기능:
    - 테마 전환 (Light/Dark)
    - QSS 컴파일 및 적용
    - Hot Reload 지원
    - 테마 변경 시그널
    """

    theme_changed = pyqtSignal(str)  # 테마 모드 문자열

    _instance: Optional['ThemeManager'] = None

    def __init__(self):
        # 이미 인스턴스가 있으면 건너뛰기
        if ThemeManager._instance is not None and ThemeManager._instance is self:
            return

        super().__init__()

        self._mode = ThemeMode.LIGHT
        self._style_loader = StyleLoader()
        self._style_compiler = StyleCompiler()
        self._compiled_qss: str = ""

        # 토큰 인스턴스
        self._light_colors = ColorTokens()
        self._dark_colors = DarkColorTokens()
        self._typography = TypographyTokens()
        self._spacing = SpacingTokens()

        # 싱글톤 인스턴스 저장
        ThemeManager._instance = self

    @property
    def mode(self) -> ThemeMode:
        """현재 테마 모드"""
        return self._mode

    @property
    def colors(self) -> ColorTokens:
        """현재 테마의 색상 토큰"""
        if self._mode == ThemeMode.DARK:
            return self._dark_colors
        return self._light_colors

    @property
    def fonts(self) -> TypographyTokens:
        """폰트 토큰"""
        return self._typography

    @property
    def spacing(self) -> SpacingTokens:
        """간격 토큰"""
        return self._spacing

    def set_theme(self, mode: ThemeMode):
        """테마 변경

        Args:
            mode: 테마 모드
        """
        if self._mode != mode:
            self._mode = mode
            self._recompile_styles()
            self._apply_to_app()
            self.theme_changed.emit(mode.value)
            print(f"[ThemeManager] Theme changed to: {mode.value}")

    def toggle_theme(self):
        """라이트/다크 토글"""
        new_mode = ThemeMode.DARK if self._mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.set_theme(new_mode)

    def get_compiled_stylesheet(self) -> str:
        """컴파일된 전체 QSS 반환"""
        if not self._compiled_qss:
            self._recompile_styles()
        return self._compiled_qss

    def apply_to_app(self, app: Optional[QApplication] = None):
        """앱 전체에 스타일 적용

        Args:
            app: QApplication 인스턴스 (None이면 현재 앱)
        """
        if app is None:
            app = QApplication.instance()

        if app:
            app.setStyleSheet(self.get_compiled_stylesheet())
            print("[ThemeManager] Stylesheet applied to app")

    def _apply_to_app(self):
        """내부용: 현재 앱에 스타일 적용"""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(self._compiled_qss)

    def _recompile_styles(self):
        """QSS 재컴파일"""
        # 기본 QSS 로드
        raw_qss = self._style_loader.load_all()

        # 테마별 오버라이드 로드
        theme_qss = self._style_loader.load_theme(self._mode.value)
        if theme_qss:
            raw_qss += f'\n/* === themes/{self._mode.value}.qss === */\n'
            raw_qss += theme_qss

        # 변수 치환
        variables = self._get_variable_map()

        # 유효성 검증 (개발 모드)
        errors = self._style_compiler.validate(raw_qss, variables)
        if errors:
            for line, msg in errors:
                print(f"[ThemeManager] QSS Error line {line}: {msg}")

        # 컴파일
        self._compiled_qss = self._style_compiler.compile(raw_qss, variables)

    def _get_variable_map(self) -> Dict[str, str]:
        """현재 테마의 변수 맵 생성"""
        variables = {}

        # 색상 토큰
        variables.update(self.colors.to_variable_map())

        # 타이포그래피 토큰
        variables.update(self._typography.to_variable_map())

        # 간격 토큰
        variables.update(self._spacing.to_variable_map())

        return variables

    def enable_hot_reload(self, enabled: bool = True):
        """Hot Reload 활성화

        Args:
            enabled: True면 QSS 파일 변경 시 자동 리로드
        """
        self._style_loader.set_hot_reload(enabled)

        if enabled:
            # 시그널 연결 (중복 방지)
            try:
                self._style_loader.file_changed.disconnect(self._on_qss_changed)
            except TypeError:
                pass
            self._style_loader.file_changed.connect(self._on_qss_changed)
            print("[ThemeManager] Hot Reload enabled")
        else:
            try:
                self._style_loader.file_changed.disconnect(self._on_qss_changed)
            except TypeError:
                pass
            print("[ThemeManager] Hot Reload disabled")

    def _on_qss_changed(self, path: str):
        """QSS 파일 변경 감지"""
        self._style_loader.invalidate_cache()
        self._recompile_styles()
        self._apply_to_app()
        self.theme_changed.emit(self._mode.value)

    def reload(self):
        """수동 리로드"""
        self._style_loader.invalidate_cache()
        self._recompile_styles()
        self._apply_to_app()

    # === 하위 호환성: 기존 Theme 클래스와 유사한 인터페이스 ===

    def get_global_stylesheet(self) -> str:
        """기존 Theme.get_global_stylesheet() 호환용

        주의: 이 메서드 대신 get_compiled_stylesheet() 사용 권장
        """
        return self.get_compiled_stylesheet()


# 편의를 위한 전역 접근 함수
def get_theme_manager() -> ThemeManager:
    """ThemeManager 싱글톤 인스턴스 반환"""
    if ThemeManager._instance is None:
        ThemeManager._instance = ThemeManager()
    return ThemeManager._instance
