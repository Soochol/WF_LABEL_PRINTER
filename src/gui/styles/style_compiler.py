"""QSS 템플릿 컴파일러 - 변수 치환"""

import re
from typing import Dict, List, Tuple


class StyleCompiler:
    """QSS 템플릿 변수 치환 컴파일러

    QSS는 CSS 변수를 지원하지 않으므로 @variable 패턴을 사용하여
    컴파일 시점에 실제 값으로 치환합니다.

    예:
        @primary → #2563EB
        @font-body → 14px
    """

    # 변수 패턴: @로 시작하는 케밥케이스 (예: @primary-dark, @font-h1)
    VARIABLE_PATTERN = re.compile(r'@([a-zA-Z][a-zA-Z0-9-]*)')

    def compile(self, raw_qss: str, variables: Dict[str, str]) -> str:
        """QSS 템플릿을 실제 값으로 치환

        Args:
            raw_qss: 변수가 포함된 QSS 템플릿 문자열
            variables: 변수 맵 {'@primary': '#2563EB', ...}

        Returns:
            치환된 QSS 문자열
        """
        def replace_variable(match):
            var_name = f'@{match.group(1)}'
            value = variables.get(var_name)
            if value is None:
                # 정의되지 않은 변수는 그대로 유지 (디버깅용)
                print(f"[StyleCompiler] Warning: undefined variable {var_name}")
                return var_name
            return value

        return self.VARIABLE_PATTERN.sub(replace_variable, raw_qss)

    def validate(self, raw_qss: str, variables: Dict[str, str]) -> List[Tuple[int, str]]:
        """미정의 변수 검출

        Args:
            raw_qss: QSS 템플릿 문자열
            variables: 변수 맵

        Returns:
            [(line_number, error_message), ...]
        """
        errors = []
        used_vars = set(self.VARIABLE_PATTERN.findall(raw_qss))
        defined_vars = set(k[1:] for k in variables.keys())  # @ 제거

        undefined = used_vars - defined_vars
        if undefined:
            for var in undefined:
                # 해당 변수가 사용된 라인 찾기
                for i, line in enumerate(raw_qss.split('\n'), 1):
                    if f'@{var}' in line:
                        errors.append((i, f"Undefined variable: @{var}"))

        return errors

    def minify(self, qss: str) -> str:
        """QSS 최소화 (공백/주석 제거)

        프로덕션 빌드용으로 파일 크기를 줄입니다.
        """
        # 주석 제거 (/* ... */)
        qss = re.sub(r'/\*.*?\*/', '', qss, flags=re.DOTALL)

        # 불필요한 공백 제거
        lines = []
        for line in qss.split('\n'):
            line = line.strip()
            if line:
                # 여러 공백을 하나로
                line = re.sub(r'\s+', ' ', line)
                lines.append(line)

        return ' '.join(lines)
