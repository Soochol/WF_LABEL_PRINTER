# PRN 파일 분석

## 파일 정보
- **파일명**: PSA_LABEL_ZPL_with_mac_address.prn
- **형식**: ZPL (Zebra Programming Language)
- **라벨 크기**: 480 x 240 dots (약 60mm x 30mm)

## ZPL 구조 분석

### 헤더 섹션 (라인 1-18)
```zpl
CT~~CD,~CC^~CT~
^XA
~TA000
~JSN
^LT0
^MNW
^MTT
^PON
^PMN
^LH0,0
^JMA
^PR1,1
~SD28
^JUS
^LRN
^CI27
^PA0,1,1,0
^XZ
```

#### 주요 명령어 설명
- `^XA`: 라벨 시작
- `^LT0`: 라벨 상단 위치 (0)
- `^MNW`: 미디어 추적 모드 (Web sensing)
- `^MTT`: 미디어 타입 (Thermal transfer)
- `^PON`: 인쇄 방향 (Normal)
- `^LH0,0`: 라벨 홈 위치 (0,0)
- `^PR1,1`: 인쇄 속도 (1 inch/sec)
- `^CI27`: 문자 인코딩 (UTF-8)
- `^XZ`: 라벨 종료

### 본문 섹션 (라인 19-38)

#### 라벨 설정
```zpl
^XA
^MMT           # 인쇄 모드: Tear-off
^PW480         # 인쇄 너비: 480 dots
^LL240         # 라벨 길이: 240 dots
^LS0           # 라벨 시프트: 0
```

#### 고정 텍스트 (라인 24-30)
```zpl
^FT17,33^A0N,20,20^FH\^CI28^FDNAME : ACTIVE WEARABLE SUITE^FS^CI27
^FT17,61^A0N,20,20^FH\^CI28^FDMODEL : WITHFORCE A10^FS^CI27
^FT17,88^A0N,20,20^FH\^CI28^FDMANUFACTURED : WITHFORCE INC.^FS^CI27
^FT17,116^A0N,20,20^FH\^CI28^FDMANUFACTURING DATE : ^FS^CI27
^FT17,144^A0N,20,20^FH\^CI28^FDS/N : ^FS^CI27
^FT15,194^A0N,20,20^FH\^CI28^FDMADE IN KOREA^FS^CI27
^FT15,219^A0N,20,20^FH\^CI28^FDA/S : 031) 426-2301^FS^CI27
```

**명령어 분석**:
- `^FT17,33`: 필드 위치 (x=17, y=33 dots)
- `^A0N,20,20`: 폰트 (0=기본폰트, Normal, 가로20, 세로20)
- `^FH\`: 16진수 값 사용 가능
- `^CI28`: UTF-8 인코딩 시작
- `^FD...^FS`: 필드 데이터
- `^CI27`: 원래 인코딩으로 복귀

#### 변수 필드

##### 1. VAR_DATE (라인 34)
```zpl
^FT245,116^A0N,20,20^FH\^CI28^FDVAR_DATE^FS^CI27
```
- **위치**: (245, 116)
- **크기**: 20x20
- **용도**: 제조 날짜
- **형식**: YYYY.MM.DD (예: 2025.10.17)
- **표시 위치**: "MANUFACTURING DATE : " 뒤

##### 2. VAR_SERIALNUMBER (라인 33)
```zpl
^FT62,145^A0N,20,20^FH\^CI28^FDVAR_SERIALNUMBER^FS^CI27
```
- **위치**: (62, 145)
- **크기**: 20x20
- **용도**: 시리얼 번호
- **형식**: P10DL0S0H3A00B03 (16자)
- **표시 위치**: "S/N : " 뒤

##### 3. VAR_2DBARCODE (라인 31-32)
```zpl
^FT197,237^BQN,2,3
^FH\^FDVAR_2DBARCODE^FS
```
- **위치**: (197, 237)
- **바코드 타입**: QR Code (`^BQ`)
- **파라미터**:
  - N: Normal orientation
  - 2: Model 2 (표준 QR Code)
  - 3: Magnification factor (크기)
- **데이터**: 시리얼 번호와 동일
- **예시**: P10DL0S0H3A00B03

##### 4. VAR_MAC (라인 35-36)
```zpl
^BY1,3,69^FT285,222^BCN,,Y,N,,A
^FDVAR_MAC^FS
```
- **위치**: (285, 222)
- **바코드 타입**: Code 128 (`^BC`)
- **파라미터**:
  - `^BY1,3,69`: 바코드 모듈 너비, 비율, 높이
  - N: Normal orientation
  - Y: 바코드 아래 텍스트 출력
  - N: UCC check digit 없음
  - A: Mode A (대문자, 숫자)
- **데이터**: MAC 주소 (device id)
- **예시**: PSAD0CF1327829495

#### 종료 명령 (라인 37-38)
```zpl
^PQ1,,,Y       # 출력 수량: 1장, 재출력 가능
^XZ            # 라벨 종료
```

## 변수 치환 전략

### 치환 방법
Python 문자열 replace() 메소드 사용:

```python
def replace_variables(template: str, date: str, serial: str, mac: str) -> str:
    zpl = template
    zpl = zpl.replace("VAR_DATE", date)
    zpl = zpl.replace("VAR_SERIALNUMBER", serial)
    zpl = zpl.replace("VAR_2DBARCODE", serial)  # S/N과 동일
    zpl = zpl.replace("VAR_MAC", mac)
    return zpl
```

### 치환 예시

**Before (템플릿)**:
```zpl
^FT245,116^A0N,20,20^FH\^CI28^FDVAR_DATE^FS^CI27
^FT62,145^A0N,20,20^FH\^CI28^FDVAR_SERIALNUMBER^FS^CI27
^FT197,237^BQN,2,3^FH\^FDVAR_2DBARCODE^FS
^BY1,3,69^FT285,222^BCN,,Y,N,,A^FDVAR_MAC^FS
```

**After (치환 후)**:
```zpl
^FT245,116^A0N,20,20^FH\^CI28^FD2025.10.17^FS^CI27
^FT62,145^A0N,20,20^FH\^CI28^FDP10DL0S0H3A00B03^FS^CI27
^FT197,237^BQN,2,3^FH\^FDP10DL0S0H3A00B03^FS
^BY1,3,69^FT285,222^BCN,,Y,N,,A^FDPSAD0CF1327829495^FS
```

## 라벨 레이아웃

```
┌─────────────────────────────────────────────────┐
│ NAME : ACTIVE WEARABLE SUITE                    │
│ MODEL : WITHFORCE A10                           │
│ MANUFACTURED : WITHFORCE INC.                   │
│ MANUFACTURING DATE : 2025.10.17                 │
│ S/N : P10DL0S0H3A00B03                          │
│                                                 │
│ MADE IN KOREA                   ┌─────────┐    │
│ A/S : 031) 426-2301             │  QR     │    │
│                                 │  CODE   │    │
│                    ║║║║║║║║║║║  └─────────┘    │
│                    PSAD0CF...                   │
└─────────────────────────────────────────────────┘
  480 dots (60mm)
```

## ZPL 명령어 레퍼런스

### 텍스트 명령어
| 명령어 | 설명 | 예시 |
|-------|------|------|
| `^FT` | Field Typeset (위치) | `^FT17,33` |
| `^A0` | 폰트 선택 | `^A0N,20,20` |
| `^FD...^FS` | Field Data | `^FDHello^FS` |
| `^CI` | 문자 인코딩 | `^CI28` (UTF-8) |

### 바코드 명령어
| 명령어 | 설명 | 타입 |
|-------|------|------|
| `^BQ` | QR Code | 2D 바코드 |
| `^BC` | Code 128 | 1D 바코드 |
| `^BY` | 바코드 필드 기본값 | 너비/비율/높이 |

### 라벨 제어
| 명령어 | 설명 | 값 |
|-------|------|-----|
| `^PW` | Print Width | 480 dots |
| `^LL` | Label Length | 240 dots |
| `^PQ` | Print Quantity | 1 |

## 주의사항

1. **문자 인코딩**: UTF-8 사용 (`^CI28`)
2. **좌표계**: 원점 (0,0)은 좌측 상단
3. **단위**: dots (1mm ≈ 8 dots @ 203dpi)
4. **바코드 데이터**: 특수문자 포함 시 `^FH\` 사용
