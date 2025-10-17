# 시리얼 번호 구조

## 개요
LOT 정보를 기반으로 자동 생성되는 고유 시리얼 번호

## 시리얼 번호 형식

### 전체 구조
```
P10  D  L0  S0  H3  A0  0  B04
│    │  │   │   │   │   │  └─ 생산순서 (3자리)
│    │  │   │   │   │   └─── Reserved 0 (1자리)
│    │  │   │   │   └────── 완제품 조립 위치 코드 (2자리)
│    │  │   │   └──────────── 제어기 HW 코드 (2자리)
│    │  │   └──────────────── Suite 사양 코드 (2자리)
│    │  └──────────────────── 로봇 사양 코드 (2자리)
│    └─────────────────────── 개발 코드 (1자리)
└──────────────────────────── 모델명 코드 (3자리)

총 16자리
```

### 예시
- `P10DL0S0H3A00B03`
- `P10DL0S0H3A00B04`
- `P10DL0S0H3A00C01`

## 구성 요소 상세

### 1. 모델명 코드 (3자리)
- **위치**: 1-3
- **형식**: 영문자 + 숫자
- **예시**:
  - `P10` - PSA 1.0
  - `W10` - WSP 1.0
  - `M10` - M10
  - `A10` - PSA 1.0

### 2. 개발 코드 (1자리)
- **위치**: 4
- **형식**: 영문자
- **예시**:
  - `P` - Pilot (파일럿)
  - `M` - Manufacturing (양산)
  - `T` - Test (테스트)
  - `D` - Demo (데모)
  - `R` - Replacement (교체품)

### 3. 로봇 사양 코드 (2자리)
- **위치**: 5-6
- **형식**: L + 숫자
- **예시**:
  - `L0` - L230-A39 (LMA & ROBOT)
  - `L1` - L210-A39
  - `L2` - L220-A39
  - `L3` - L220-A43
  - `L4` - L220-A47
  - `L5` - L200-39
  - `L6` - L200-43
  - `L7` - L200-47
  - `L8` - 추가 사양...

### 4. Suite 사양 코드 (2자리)
- **위치**: 7-8
- **형식**: S + 숫자
- **예시**:
  - `S0` - 초기샘플 (Suite)
  - `S1` - 사양1
  - `S2` - 사양2

### 5. 제어기 HW 코드 (2자리)
- **위치**: 9-10
- **형식**: H + 숫자
- **예시**:
  - `H1` - New
  - `H2` - 버전2
  - `H3` - 버전3
  - `H4` - 버전4

### 6. 완제품 조립 위치 코드 (2자리)
- **위치**: 11-12
- **형식**: A + 숫자
- **예시**:
  - `A0` - 완제품 조립 + 화성시 1라인 (동탄)
  - `A1` - LMA 조립 + 화성시 1라인 (동탄)

### 7. Reserved 0 (1자리)
- **위치**: 13
- **형식**: 숫자
- **값**: 고정값 `0`
- **용도**: 향후 확장 또는 체크섬

### 8. 생산순서 (3자리)
- **위치**: 14-16
- **형식**: 영문자 + 숫자 2자리
- **범위**:
  - A00 - A99 (100개)
  - B00 - B99 (100개)
  - C00 - Z99
- **자동 증가 규칙**:
  ```
  B03 → B04 → B05 → ... → B99 → C00 → C01 → ...
  ```

## LOT 번호 vs 시리얼 번호

### LOT 번호
- **정의**: 동일한 사양으로 생산되는 배치를 식별
- **구성**: 시리얼 번호의 처음 13자리
- **예시**: `P10DL0S0H3A00` (고정값)

### 시리얼 번호
- **정의**: 개별 제품을 고유하게 식별
- **구성**: LOT 번호 + 생산순서
- **예시**: `P10DL0S0H3A00B03` (LOT + 생산순서)

## 자동 증가 로직

### 알고리즘
```python
def increment_counter(current: str) -> str:
    """
    생산순서 카운터 증가

    Args:
        current: 현재 카운터 (예: "B03")

    Returns:
        증가된 카운터 (예: "B04")
    """
    letter = current[0]  # 'B'
    number = int(current[1:])  # 3

    if number < 99:
        # 숫자만 증가: B03 → B04
        return f"{letter}{number+1:02d}"
    else:
        # 다음 알파벳으로 넘어감: B99 → C00
        next_letter = chr(ord(letter) + 1)
        if next_letter > 'Z':
            raise ValueError("카운터 범위 초과 (Z99)")
        return f"{next_letter}00"
```

### 예시 시퀀스
```
LOT: P10DL0S0H3A00

생산 1: P10DL0S0H3A00A00
생산 2: P10DL0S0H3A00A01
생산 3: P10DL0S0H3A00A02
...
생산 100: P10DL0S0H3A00A99
생산 101: P10DL0S0H3A00B00
생산 102: P10DL0S0H3A00B01
...
생산 200: P10DL0S0H3A00B99
생산 201: P10DL0S0H3A00C00
```

### 카운터 범위
- **최소**: A00
- **최대**: Z99
- **총 개수**: 26 × 100 = 2,600개

## 데이터베이스 저장

### LOT 설정 테이블
```sql
CREATE TABLE lot_config (
    id INTEGER PRIMARY KEY,
    model_code TEXT NOT NULL,      -- P10
    dev_code TEXT NOT NULL,        -- D
    robot_spec TEXT NOT NULL,      -- L0
    suite_spec TEXT NOT NULL,      -- S0
    hw_code TEXT NOT NULL,         -- H3
    assembly_code TEXT NOT NULL,   -- A0
    reserved TEXT NOT NULL,        -- 0
    counter TEXT NOT NULL,         -- B03
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 시리얼 번호 생성
```python
def generate_serial_number(lot_config: dict) -> str:
    """LOT 설정으로부터 시리얼 번호 생성"""
    return (
        f"{lot_config['model_code']}"
        f"{lot_config['dev_code']}"
        f"{lot_config['robot_spec']}"
        f"{lot_config['suite_spec']}"
        f"{lot_config['hw_code']}"
        f"{lot_config['assembly_code']}"
        f"{lot_config['reserved']}"
        f"{lot_config['counter']}"
    )
```

## 검증 규칙

### 형식 검증
```python
import re

SERIAL_NUMBER_PATTERN = re.compile(
    r'^[A-Z]\d{2}'     # 모델명: P10
    r'[A-Z]'           # 개발코드: D
    r'[A-Z]\d'         # 로봇사양: L0
    r'[A-Z]\d'         # Suite사양: S0
    r'[A-Z]\d'         # HW코드: H3
    r'[A-Z]\d'         # 조립코드: A0
    r'\d'              # Reserved: 0
    r'[A-Z]\d{2}$'     # 생산순서: B03
)

def validate_serial_number(sn: str) -> bool:
    """시리얼 번호 형식 검증"""
    if len(sn) != 16:
        return False
    return SERIAL_NUMBER_PATTERN.match(sn) is not None
```

### 중복 검사
```python
def check_duplicate(serial_number: str, db) -> bool:
    """이미 출력된 시리얼 번호인지 확인"""
    result = db.query(
        "SELECT COUNT(*) FROM print_history WHERE serial_number = ?",
        (serial_number,)
    )
    return result[0][0] > 0
```

## GUI 입력 폼 설계

### 드롭다운 메뉴
```python
# 모델명 코드
model_codes = ["P10", "W10", "M10", "A10"]

# 개발 코드
dev_codes = ["P", "M", "T", "D", "R"]

# 로봇 사양 코드
robot_specs = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]

# Suite 사양 코드
suite_specs = ["S0", "S1", "S2"]

# HW 코드
hw_codes = ["H1", "H2", "H3", "H4"]

# 조립 코드
assembly_codes = ["A0", "A1"]

# Reserved (고정값)
reserved = "0"

# 생산순서 (자동 증가)
# 시작값 입력 가능, 이후 자동 증가
```

## 사용 사례

### 케이스 1: 신규 LOT 시작
```
사용자 입력:
  - 모델명: P10
  - 개발코드: D
  - 로봇사양: L0
  - Suite사양: S0
  - HW코드: H3
  - 조립코드: A0
  - 시작번호: A00

생성된 시리얼:
  1번째: P10DL0S0H3A00A00
  2번째: P10DL0S0H3A00A01
  3번째: P10DL0S0H3A00A02
```

### 케이스 2: LOT 변경 (사양 변경)
```
기존 LOT: P10DL0S0H3A00
새 LOT: P10DL0S1H3A00 (Suite 사양 변경: S0 → S1)

카운터 리셋: A00부터 다시 시작
```

### 케이스 3: 카운터만 변경
```
같은 LOT에서 중간 번호부터 시작:
  LOT: P10DL0S0H3A00
  시작번호: B50

생성된 시리얼:
  P10DL0S0H3A00B50
  P10DL0S0H3A00B51
  ...
```
