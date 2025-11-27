"""QSS 파일 로더 + Hot Reload"""

from pathlib import Path
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QFileSystemWatcher


class StyleLoader(QObject):
    """QSS 파일 로더

    기능:
    - QSS 파일을 순서대로 로드하여 하나의 문자열로 결합
    - QFileSystemWatcher를 통한 Hot Reload 지원
    - 파일 변경 시 시그널 발생
    """

    file_changed = pyqtSignal(str)  # 변경된 파일 경로

    # QSS 파일 로드 순서 (의존성 순서)
    LOAD_ORDER = [
        'base/_reset.qss',
        'base/_global.qss',
        'components/_buttons.qss',
        'components/_inputs.qss',
        'components/_cards.qss',
        'components/_tables.qss',
        'components/_status.qss',
        'components/_sidebar.qss',
        'components/_containers.qss',
        'components/_trees.qss',
        'components/_views.qss',
    ]

    def __init__(self, qss_dir: Optional[Path] = None):
        """
        Args:
            qss_dir: QSS 파일이 위치한 디렉토리 (기본: styles/qss)
        """
        super().__init__()

        if qss_dir is None:
            qss_dir = Path(__file__).parent / 'qss'
        self._qss_dir = qss_dir

        self._watcher = QFileSystemWatcher()
        self._hot_reload_enabled = False
        self._cache: Optional[str] = None

    def load_all(self) -> str:
        """모든 QSS 파일 로드 (순서 보장)

        Returns:
            결합된 QSS 문자열
        """
        if self._cache is not None and not self._hot_reload_enabled:
            return self._cache

        combined_qss = []

        for qss_path in self.LOAD_ORDER:
            full_path = self._qss_dir / qss_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    combined_qss.append(f'/* === {qss_path} === */')
                    combined_qss.append(content)
                except Exception as e:
                    print(f"[StyleLoader] Error loading {qss_path}: {e}")

        self._cache = '\n'.join(combined_qss)
        return self._cache

    def load_theme(self, theme_name: str) -> str:
        """테마별 오버라이드 QSS 로드

        Args:
            theme_name: 테마 이름 (예: 'light', 'dark')

        Returns:
            테마 QSS 문자열
        """
        theme_path = self._qss_dir / 'themes' / f'{theme_name}.qss'
        if theme_path.exists():
            try:
                return theme_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"[StyleLoader] Error loading theme {theme_name}: {e}")
        return ''

    def get_all_qss_files(self) -> List[Path]:
        """모든 QSS 파일 경로 반환"""
        if not self._qss_dir.exists():
            return []
        return list(self._qss_dir.rglob('*.qss'))

    def set_hot_reload(self, enabled: bool):
        """Hot Reload 설정

        Args:
            enabled: True면 파일 변경 감시 활성화
        """
        self._hot_reload_enabled = enabled

        if enabled:
            self._setup_file_watcher()
        else:
            # 기존 감시 제거
            files = self._watcher.files()
            if files:
                self._watcher.removePaths(files)
            dirs = self._watcher.directories()
            if dirs:
                self._watcher.removePaths(dirs)

    def _setup_file_watcher(self):
        """파일 감시 설정"""
        # 기존 감시 제거
        files = self._watcher.files()
        if files:
            self._watcher.removePaths(files)

        # QSS 파일 감시
        qss_files = self.get_all_qss_files()
        for qss_file in qss_files:
            self._watcher.addPath(str(qss_file))

        # 시그널 연결 (중복 방지)
        try:
            self._watcher.fileChanged.disconnect(self._on_file_changed)
        except TypeError:
            pass
        self._watcher.fileChanged.connect(self._on_file_changed)

    def _on_file_changed(self, path: str):
        """파일 변경 시 호출"""
        # 캐시 무효화
        self._cache = None

        # 파일이 삭제 후 재생성되면 watcher에서 제거되므로 다시 추가
        if path not in self._watcher.files():
            if Path(path).exists():
                self._watcher.addPath(path)

        # 시그널 발생
        self.file_changed.emit(path)
        print(f"[StyleLoader] Hot Reload: {Path(path).name}")

    def invalidate_cache(self):
        """캐시 무효화"""
        self._cache = None
