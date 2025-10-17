# 시스템 아키텍처

## 개요
Zebra 라벨 프린터를 USB로 제어하여 시리얼 번호 라벨을 자동 출력하는 시스템

## 시스템 구성도

```
┌─────────────────────────────────────────────────────────┐
│                   PyQt6 GUI Application                  │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │  Printer       │  │  Serial        │                 │
│  │  Selection     │  │  Port          │                 │
│  └────────────────┘  └────────────────┘                 │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           LOT 정보 입력 폼                       │    │
│  │  모델명│개발코드│로봇사양│Suite│HW│조립│Reserved  │    │
│  │   P10  │   D   │  L0   │ S0 │H3│A0 │   0      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  생산순서: B03 (자동증가)                                │
│  현재 S/N: P10DL0S0H3A00B03                              │
│  MAC 주소: [자동수신대기중...]                           │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │ [🖨️ 출력] [📝 테스트] [✏️ 수동출력]        │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ MCU 로그:                                        │    │
│  │ device id: PSAD0CF1327829495                    │    │
│  │ MAC detected!                                   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 출력 이력:                                       │    │
│  │ 시간      │ S/N              │ MAC             │    │
│  │ 10:53:42  │ P10DL0S0H3A00B03 │ PSAD0C...       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼──────┐       ┌───────▼──────────┐
│ Printer      │       │ Serial           │
│ Controller   │       │ Monitor          │
│ (USB/ZPL)    │       │ (MCU 통신)        │
└───────┬──────┘       └───────┬──────────┘
        │                       │
        │              ┌────────▼─────────┐
        │              │ MAC Address      │
        │              │ Parser           │
        │              └────────┬─────────┘
        │                       │
┌───────▼───────────────────────▼─────────┐
│         Database (SQLite)               │
│  - 출력 이력                             │
│  - LOT 설정                             │
│  - 시리얼 번호 카운터                    │
└─────────────────────────────────────────┘
```

## 컴포넌트 설명

### 1. GUI Layer (PyQt6)
- **main_window.py**: 메인 애플리케이션 윈도우
- **lot_input_widget.py**: LOT 정보 입력 폼
- **serial_monitor_widget.py**: MCU 시리얼 로그 표시
- **history_widget.py**: 출력 이력 테이블

### 2. Printer Layer
- **zebra_controller.py**: USB Zebra 프린터 제어
- **prn_parser.py**: PRN 파일 파싱 및 변수 치환
- **printer_discovery.py**: 프린터 자동 검색

### 3. Serial Communication Layer
- **mcu_monitor.py**: MCU 시리얼 포트 모니터링 (QThread)
- **mac_parser.py**: device id 정규식 추출

### 4. Business Logic Layer
- **serial_number_generator.py**: 시리얼 번호 생성 및 증가
- **db_manager.py**: 데이터베이스 CRUD 작업
- **config_manager.py**: 설정 파일 관리

### 5. Data Layer
- **SQLite Database**: 출력 이력, LOT 설정, 앱 설정 저장

## 데이터 흐름

### 정상 출력 시나리오
```
1. User: LOT 정보 입력 (P10, D, L0, S0, H3, A0, 0, B03)
   ↓
2. User: [출력] 버튼 클릭
   ↓
3. System: MAC 주소 대기 상태
   ↓
4. MCU: "device id: PSAD0CF1327829495" 출력
   ↓
5. MCU Monitor: 정규식으로 MAC 추출
   ↓
6. Serial Number Generator: "P10DL0S0H3A00B03" 생성
   ↓
7. PRN Parser:
   - VAR_DATE → "2025.10.17"
   - VAR_SERIALNUMBER → "P10DL0S0H3A00B03"
   - VAR_2DBARCODE → "P10DL0S0H3A00B03" (QR Code)
   - VAR_MAC → "PSAD0CF1327829495" (Code 128)
   ↓
8. Zebra Controller: ZPL 명령 전송 → 프린터 출력
   ↓
9. DB Manager: 출력 이력 저장
   ↓
10. Serial Number Generator: 카운터 증가 (B03 → B04)
    ↓
11. GUI: 화면 업데이트
```

## 기술 스택

| 레이어 | 기술 |
|-------|------|
| GUI | PyQt6 |
| 프린터 통신 | pyusb (USB Raw 통신) |
| 시리얼 통신 | pyserial |
| 데이터베이스 | SQLite3 |
| 설정 관리 | PyYAML |
| 로깅 | Python logging |
| 테스트 | pytest, pytest-qt |

## 외부 의존성

### 하드웨어
- Zebra 라벨 프린터 (USB 연결)
- MCU 디바이스 (시리얼 포트 연결)

### 라이브러리
- Python 3.9+
- PyQt6 6.6+
- pyusb 1.2+
- pyserial 3.5+

## 보안 고려사항

1. **데이터 무결성**
   - 출력 이력 백업
   - 트랜잭션 관리

2. **에러 복구**
   - 프린터 연결 끊김 감지
   - 시리얼 포트 재연결
   - DB 잠금 처리

3. **데이터 검증**
   - MAC 주소 형식 검증
   - 시리얼 번호 중복 체크
