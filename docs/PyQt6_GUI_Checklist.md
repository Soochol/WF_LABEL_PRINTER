# PyQt6 GUI 개발 완벽 체크리스트

AI에게 이 체크리스트를 제공하고 준수하도록 요청하세요.

---

## 📐 1. 레이아웃 구조 (LAYOUT STRUCTURE)

### ✓ 절대 위치 배치 금지
- `setGeometry()`, `move()`, `resize()` 사용 금지
- 모든 위젯은 레이아웃 매니저로만 배치
- 예외: 최상위 QMainWindow의 `setMinimumSize()`만 허용

### ✓ 중앙 위젯 설정 필수
- QMainWindow 사용 시 반드시 `setCentralWidget()` 호출
- 중앙 위젯에 메인 레이아웃 설정

**예시:**
```python
central_widget = QWidget()
self.setCentralWidget(central_widget)
main_layout = QVBoxLayout()
central_widget.setLayout(main_layout)
```

### ✓ 레이아웃 계층 명확화
- 중첩된 레이아웃은 들여쓰기로 구조 표시
- 각 레이아웃 선언 시 주석으로 용도 명시

**예시:**
```python
# 메인 레이아웃 (수직)
main_layout = QVBoxLayout()

    # 상단 영역 (수평)
    top_layout = QHBoxLayout()
    main_layout.addLayout(top_layout)
    
        # 왼쪽 버튼 그룹
        left_buttons = QVBoxLayout()
        top_layout.addLayout(left_buttons)
```

---

## 📦 2. 위젯 추가 규칙 (WIDGET ADDITION)

### ✓ 모든 위젯은 반드시 레이아웃에 추가
- 위젯 생성 후 즉시 `addWidget()` 호출
- 고아 위젯(orphan widget) 절대 금지

**❌ 잘못된 예:**
```python
button = QPushButton("클릭")  # 어디에도 추가 안 됨!
```

**✅ 올바른 예:**
```python
button = QPushButton("클릭")
layout.addWidget(button)  # 즉시 추가
```

### ✓ 위젯 추가 시 stretch factor 명시
- `addWidget(widget, stretch, alignment)`
- stretch 기본값은 0 (고정 크기)

**예시:**
```python
layout.addWidget(title_label, 0)        # 고정 크기
layout.addWidget(content_text, 1)       # 남은 공간 차지
layout.addWidget(status_label, 0)       # 고정 크기
```

### ✓ addStretch() 적극 활용
- 여백이 필요한 곳에 `addStretch()` 사용
- 위젯을 한쪽으로 밀 때 유용

**예시:**
```python
layout.addWidget(button1)
layout.addStretch()  # 버튼을 위로 밀어올림
```

---

## 📏 3. 크기 설정 (SIZE MANAGEMENT)

### ✓ 최상위 윈도우 크기 설정
- `setMinimumSize(width, height)` 필수
- `resize()`로 초기 크기도 설정

**예시:**
```python
self.setMinimumSize(800, 600)
self.resize(1024, 768)
```

### ✓ 개별 위젯 최소/최대 크기 지정
- 고정 높이 위젯: `setFixedHeight()`
- 최소 크기: `setMinimumSize()`
- 최대 크기: `setMaximumSize()`
- 고정 크기: `setFixedSize()`

**예시:**
```python
title_label.setFixedHeight(50)
button.setMinimumSize(100, 30)
sidebar.setMaximumWidth(250)
icon.setFixedSize(32, 32)
```

### ✓ 크기 정책(Size Policy) 설정
- `setSizePolicy(horizontal, vertical)`
- 일반적인 조합:
  - `QSizePolicy.Policy.Expanding` - 가능한 한 늘어남
  - `QSizePolicy.Policy.Fixed` - 고정 크기
  - `QSizePolicy.Policy.Minimum` - 최소 크기 유지
  - `QSizePolicy.Policy.Preferred` - 선호 크기

**예시:**
```python
from PyQt6.QtWidgets import QSizePolicy
text_edit.setSizePolicy(
    QSizePolicy.Policy.Expanding,
    QSizePolicy.Policy.Expanding
)
```

---

## 🎨 4. 간격 및 여백 (SPACING & MARGINS)

### ✓ 레이아웃 여백(Margin) 설정
- `setContentsMargins(left, top, right, bottom)`
- 일반 윈도우: 10~20px
- 다이얼로그: 15~25px
- 패널/그룹: 5~10px

**예시:**
```python
main_layout.setContentsMargins(15, 15, 15, 15)
panel_layout.setContentsMargins(10, 10, 10, 10)
```

### ✓ 위젯 간격(Spacing) 설정
- `setSpacing(pixels)`
- 일반적으로 5~15px

**예시:**
```python
layout.setSpacing(10)
```

### ✓ 개별 위젯 간격
- `addSpacing(pixels)` 사용
- `addStretch(stretch_factor)` 사용

**예시:**
```python
layout.addWidget(button1)
layout.addSpacing(20)  # 20px 간격
layout.addWidget(button2)
```

---

## 🔍 5. 디버깅 및 시각화 (DEBUGGING)

### ✓ 개발 중 배경색 설정
- 각 주요 위젯/레이아웃에 배경색 지정
- 레이아웃 경계를 시각적으로 확인
- 완성 후 제거

**예시:**
```python
# 개발 중
central_widget.setStyleSheet("background-color: #f0f0f0;")
top_widget.setStyleSheet("background-color: lightblue;")
bottom_widget.setStyleSheet("background-color: lightgreen;")

# 또는 더 세밀하게
self.setStyleSheet('''
    QWidget#centralWidget { background-color: #f0f0f0; }
    QWidget#topPanel { background-color: lightblue; border: 1px solid blue; }
    QWidget#bottomPanel { background-color: lightgreen; border: 1px solid green; }
''')
```

### ✓ 위젯에 objectName 설정
- 디버깅과 스타일시트 적용에 유용

**예시:**
```python
central_widget.setObjectName("centralWidget")
top_panel.setObjectName("topPanel")
```

### ✓ 크기 정보 출력 함수 추가

**예시:**
```python
def print_widget_info(self):
    print(f"Window: {self.size()}")
    print(f"Central: {self.central_widget.size()}")
    print(f"Button: {self.button.size()}, visible: {self.button.isVisible()}")
```

---

## 🎯 6. 정렬 및 배치 (ALIGNMENT)

### ✓ 위젯 정렬 명시
- `addWidget()` 세 번째 인자로 정렬 지정
- `Qt.AlignmentFlag` 사용

**예시:**
```python
from PyQt6.QtCore import Qt
layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
layout.addWidget(button, 0, Qt.AlignmentFlag.AlignRight)
```

### ✓ 일반적인 정렬 조합
- `AlignLeft`, `AlignRight`, `AlignCenter` (수평)
- `AlignTop`, `AlignBottom`, `AlignVCenter` (수직)
- `AlignTop | AlignLeft` (조합 가능)

### ✓ 레이아웃 정렬
- `setAlignment()` 사용

**예시:**
```python
button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
```

---

## 📱 7. 반응형 설계 (RESPONSIVE DESIGN)

### ✓ Stretch factor 전략적 사용
- 고정 크기 요소: stretch = 0
- 확장 가능 요소: stretch = 1 이상
- 비율: 2:1 비율이면 stretch를 2와 1로 설정

**예시:**
```python
layout.addWidget(sidebar, 1)      # 1/4 차지
layout.addWidget(main_area, 3)    # 3/4 차지
```

### ✓ QSplitter 사용 고려
- 사용자가 직접 크기 조절 가능

**예시:**
```python
splitter = QSplitter(Qt.Orientation.Horizontal)
splitter.addWidget(left_panel)
splitter.addWidget(right_panel)
splitter.setStretchFactor(0, 1)
splitter.setStretchFactor(1, 3)
```

---

## ✅ 8. 초기화 순서 (INITIALIZATION ORDER)

**반드시 이 순서를 따를 것:**

1. `super().__init__()` 호출
2. 윈도우 기본 속성 설정 (제목, 크기)
3. 중앙 위젯 생성 및 설정 (QMainWindow인 경우)
4. 메인 레이아웃 생성 및 설정
5. 하위 레이아웃들 생성
6. 위젯들 생성 및 레이아웃에 추가
7. 시그널/슬롯 연결
8. 초기 상태 설정

**예시 템플릿:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        # 1. 부모 클래스 초기화
        super().__init__()
        
        # 2. 윈도우 속성
        self.setWindowTitle("앱 이름")
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)
        
        # 3. 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 4. 메인 레이아웃
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 5-6. UI 구성
        self._setup_ui(main_layout)
        
        # 7. 연결
        self._connect_signals()
        
        # 8. 초기화
        self._initialize_state()
```

---

## 🚫 9. 절대 하지 말아야 할 것들 (DON'T)

- ❌ `setGeometry()` 사용
- ❌ `move()` 사용
- ❌ 위젯 생성 후 레이아웃 추가 안 함
- ❌ 레이아웃 없이 부모만 지정
- ❌ 크기 설정 없이 빈 레이아웃
- ❌ 중첩 레이아웃에서 부모 지정 누락
- ❌ `show()` 전에 크기/레이아웃 미설정

---

## 📝 10. 코드 작성 스타일 (CODE STYLE)

### ✓ 주석으로 구조 명시
```python
# ========== 상단 영역 ==========
# ========== 메인 콘텐츠 ==========
# ========== 하단 상태바 ==========
```

### ✓ 변수명 명확히
- `main_layout` (메인 레이아웃)
- `top_h_layout` (상단 수평 레이아웃)
- `left_v_layout` (왼쪽 수직 레이아웃)

### ✓ 들여쓰기로 계층 표현
```python
main_layout = QVBoxLayout()

    top_layout = QHBoxLayout()
    main_layout.addLayout(top_layout)
    
        button1 = QPushButton()
        top_layout.addWidget(button1)
        
        button2 = QPushButton()
        top_layout.addWidget(button2)
```

---

## 🎯 AI에게 요청하는 방법

```
"위의 체크리스트를 100% 준수하면서,
다음 구조의 GUI를 만들어줘:

- 메인 윈도우 (최소 800x600, 초기 1024x768)
- 수직 메인 레이아웃 (여백 15px, 간격 10px)
  - 제목 라벨 (고정 높이 50px, 중앙 정렬)
  - 수평 레이아웃 (간격 10px)
    - 버튼1 (최소 100x30)
    - 버튼2 (최소 100x30)
    - Stretch (남은 공간)
  - 텍스트 에디터 (stretch=1, 확장 정책)
  - 상태 라벨 (고정 높이 30px, 왼쪽 정렬)

개발 중이니 각 영역에 다른 배경색 적용해줘."
```

---

## 📚 추가 리소스

### 자주 사용하는 레이아웃
- `QVBoxLayout` - 수직 배치
- `QHBoxLayout` - 수평 배치
- `QGridLayout` - 그리드 배치
- `QFormLayout` - 폼 형식 배치
- `QStackedLayout` - 겹쳐진 페이지

### 자주 사용하는 위젯
- `QPushButton` - 버튼
- `QLabel` - 텍스트/이미지 표시
- `QLineEdit` - 한 줄 입력
- `QTextEdit` - 여러 줄 입력
- `QComboBox` - 드롭다운
- `QCheckBox` - 체크박스
- `QRadioButton` - 라디오 버튼
- `QListWidget` - 리스트
- `QTableWidget` - 테이블
- `QTreeWidget` - 트리

---

**이 체크리스트를 AI에게 제공하고 준수하도록 요청하면, 깔끔하고 정리된 PyQt6 GUI를 얻을 수 있습니다!** 🎉
