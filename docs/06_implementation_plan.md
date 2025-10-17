# 구현 계획

## 개발 로드맵

### 총 예상 시간: 약 10시간
### 개발 방식: 백엔드 우선 → GUI 통합

---

## Phase 1: 프로젝트 기본 설정 (30분)

### 1.1 디렉토리 구조 생성
```
WF_LABEL_PRINTER/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── printer/
│   │   └── __init__.py
│   ├── serial_comm/
│   │   └── __init__.py
│   ├── database/
│   │   └── __init__.py
│   ├── gui/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── templates/
│   └── PSA_LABEL_ZPL_with_mac_address.prn
├── data/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── tests/
│   └── __init__.py
├── docs/
│   └── (문서들)
├── requirements.txt
├── config.yaml
├── .gitignore
└── README.md
```

### 1.2 requirements.txt 작성
```txt
pyusb==1.2.1
pyserial==3.5
PyQt6==6.6.1
pyyaml==6.0.1
python-dateutil==2.8.2
pytest==7.4.3
pytest-qt==4.2.0
```

### 1.3 config.yaml 작성
기본 설정 파일 생성

### 1.4 .gitignore 작성
```
__pycache__/
*.py[cod]
*.db
*.log
data/*.db
logs/*.log
.vscode/
.idea/
venv/
```

### 체크리스트
- [ ] 디렉토리 구조 생성
- [ ] requirements.txt 작성
- [ ] config.yaml 작성
- [ ] .gitignore 작성
- [ ] README.md 기본 골격 작성

---

## Phase 2: 데이터베이스 모듈 (30분)

### 2.1 database/models.py
- 테이블 스키마 SQL 정의
- 초기 데이터 SQL 정의

### 2.2 database/exceptions.py
- 커스텀 예외 클래스 정의

### 2.3 database/db_manager.py
- DBManager 클래스 구현
- CRUD 메소드 구현
- 백업 기능 구현

### 2.4 테스트
```python
# tests/test_database.py
def test_db_initialization():
    db = DBManager(":memory:")
    db.initialize()
    assert db.get_lot_config() is not None
```

### 체크리스트
- [ ] models.py 작성
- [ ] exceptions.py 작성
- [ ] db_manager.py 구현
- [ ] 단위 테스트 작성
- [ ] 테스트 통과 확인

---

## Phase 3: 시리얼 번호 생성기 (20분)

### 3.1 utils/serial_number_generator.py
- SerialNumberGenerator 클래스 구현
- 카운터 증가 로직
- 검증 로직

### 3.2 테스트
```python
# tests/test_serial_number.py
def test_serial_generation():
    gen = SerialNumberGenerator()
    sn = gen.generate()
    assert len(sn) == 16
    assert sn == "P10DL0S0H3A00A00"

def test_counter_increment():
    gen = SerialNumberGenerator(counter="B99")
    gen.increment_counter()
    assert gen.counter == "C00"
```

### 체크리스트
- [ ] SerialNumberGenerator 클래스 구현
- [ ] 카운터 증가 로직 구현
- [ ] 검증 로직 구현
- [ ] 단위 테스트 작성
- [ ] 테스트 통과 확인

---

## Phase 4: PRN 파서 (30분)

### 4.1 printer/prn_parser.py
- PRNParser 클래스 구현
- 템플릿 로드
- 변수 치환 로직
- 검증 로직

### 4.2 테스트
```python
# tests/test_prn_parser.py
def test_variable_replacement():
    parser = PRNParser("templates/PSA_LABEL_ZPL_with_mac_address.prn")
    zpl = parser.replace_variables(
        "2025.10.17",
        "P10DL0S0H3A00B03",
        "PSAD0CF1327829495"
    )
    assert "VAR_DATE" not in zpl
    assert "2025.10.17" in zpl
```

### 체크리스트
- [ ] PRNParser 클래스 구현
- [ ] 변수 치환 로직 구현
- [ ] 검증 로직 구현
- [ ] 단위 테스트 작성
- [ ] 실제 PRN 파일로 테스트

---

## Phase 5: MCU 시리얼 통신 (40분)

### 5.1 serial_comm/mac_parser.py
- MACParser 클래스 구현
- 정규식 패턴 매칭
- 검증 로직

### 5.2 serial_comm/mcu_monitor.py
- MCUMonitor 클래스 구현 (QThread)
- 시리얼 포트 연결
- 로그 읽기 루프
- 시그널 발생

### 5.3 테스트
```python
# tests/test_mac_parser.py
def test_mac_parsing():
    line = "device id: PSAD0CF1327829495"
    mac = MACParser.parse(line)
    assert mac == "PSAD0CF1327829495"
```

### 체크리스트
- [ ] MACParser 구현
- [ ] MCUMonitor 구현
- [ ] 시그널 동작 확인
- [ ] 실제 MCU와 연결 테스트
- [ ] 에러 핸들링 구현

---

## Phase 6: Zebra 프린터 제어 (1시간)

### 6.1 printer/exceptions.py
- 프린터 예외 클래스 정의

### 6.2 printer/printer_discovery.py
- PrinterDiscovery 클래스 구현
- USB 프린터 검색

### 6.3 printer/zebra_controller.py
- ZebraController 클래스 구현
- USB 연결
- ZPL 전송
- 상태 조회
- 테스트 출력

### 6.4 테스트
```python
# tests/test_zebra_controller.py
def test_printer_discovery():
    printers = PrinterDiscovery.find_zebra_printers()
    assert len(printers) > 0

def test_printer_connection():
    printer = ZebraController()
    assert printer.connect() == True
    printer.disconnect()
```

### 체크리스트
- [ ] PrinterDiscovery 구현
- [ ] ZebraController 구현
- [ ] 실제 프린터와 연결 테스트
- [ ] ZPL 전송 테스트
- [ ] 테스트 라벨 출력 확인

---

## Phase 7: CLI 테스트 버전 (30분)

### 7.1 main.py (CLI 버전)
```python
# 전체 워크플로우 통합
# 1. 프린터 연결
# 2. MCU 모니터 시작
# 3. MAC 수신 대기
# 4. 시리얼 번호 생성
# 5. ZPL 생성 및 출력
# 6. DB 저장
# 7. 카운터 증가
```

### 7.2 통합 테스트
- 실제 하드웨어 연결
- 전체 프로세스 실행
- 라벨 출력 확인
- DB 이력 확인

### 체크리스트
- [ ] CLI main.py 작성
- [ ] 전체 프로세스 통합
- [ ] 실제 하드웨어로 테스트
- [ ] 에러 핸들링 검증
- [ ] 로깅 동작 확인

---

## Phase 8: PyQt6 GUI - 기본 UI (1.5시간)

### 8.1 gui/main_window.py
- 메인 윈도우 레이아웃
- 메뉴바 (파일, 설정, 도움말)
- 상태바
- 툴바

### 8.2 gui/widgets/lot_input_widget.py
- LOT 정보 입력 폼
- 드롭다운 메뉴 (code_master에서 로드)
- 생산순서 카운터 표시
- 현재 시리얼 번호 표시

### 8.3 프린터/COM 포트 선택
- 프린터 선택 콤보박스
- COM 포트 선택 콤보박스
- 새로고침 버튼

### 체크리스트
- [ ] 메인 윈도우 레이아웃 구현
- [ ] LOT 입력 폼 위젯 구현
- [ ] 프린터/포트 선택 UI 구현
- [ ] 드롭다운 데이터 바인딩
- [ ] UI 동작 테스트

---

## Phase 9: PyQt6 GUI - 시리얼 모니터 (1시간)

### 9.1 gui/widgets/serial_monitor_widget.py
- 로그 텍스트 에리어
- MAC 주소 하이라이트
- 자동 스크롤
- 클리어 버튼

### 9.2 MCUMonitor 연동
- 시그널 연결
- 실시간 로그 표시
- MAC 주소 자동 감지

### 체크리스트
- [ ] 시리얼 모니터 위젯 구현
- [ ] MCUMonitor 시그널 연결
- [ ] 로그 하이라이팅 구현
- [ ] 자동 스크롤 동작 확인
- [ ] 실제 MCU 연결 테스트

---

## Phase 10: PyQt6 GUI - 출력 기능 (1.5시간)

### 10.1 출력 버튼
- [출력] 버튼 클릭 이벤트
- MAC 대기 상태 표시
- 프로그레스 다이얼로그
- 출력 완료 메시지

### 10.2 gui/dialogs/test_print_dialog.py
- 테스트 출력 다이얼로그
- 더미 데이터 입력
- 즉시 출력

### 10.3 gui/dialogs/manual_print_dialog.py
- 수동 텍스트 출력 다이얼로그
- ZPL 명령 직접 입력
- 출력 버튼

### 체크리스트
- [ ] 출력 버튼 이벤트 구현
- [ ] 전체 출력 플로우 연동
- [ ] 테스트 출력 대화상자 구현
- [ ] 수동 출력 대화상자 구현
- [ ] 에러 처리 및 사용자 피드백

---

## Phase 11: PyQt6 GUI - 출력 이력 (1시간)

### 11.1 gui/widgets/history_widget.py
- 출력 이력 테이블 뷰
- 컬럼: 시간, S/N, MAC, 상태
- 페이지네이션

### 11.2 검색 및 필터
- 날짜 범위 선택
- 시리얼 번호 검색
- 필터 적용

### 11.3 CSV 내보내기
- 현재 필터된 데이터 내보내기

### 체크리스트
- [ ] 이력 테이블 위젯 구현
- [ ] 검색/필터 기능 구현
- [ ] CSV 내보내기 구현
- [ ] 페이지네이션 구현
- [ ] 데이터 새로고침

---

## Phase 12: 통합 및 테스트 (1.5시간)

### 12.1 전체 기능 통합
- 모든 모듈 연동 확인
- 시나리오 테스트

### 12.2 에러 핸들링 강화
- 예외 처리 추가
- 사용자 친화적 메시지
- 로깅 강화

### 12.3 UI/UX 개선
- 레이아웃 조정
- 단축키 추가
- 툴팁 추가

### 12.4 성능 최적화
- DB 쿼리 최적화
- GUI 응답성 개선

### 체크리스트
- [ ] 전체 시나리오 테스트
- [ ] 에러 케이스 테스트
- [ ] 성능 테스트
- [ ] UI/UX 개선
- [ ] 최종 버그 수정

---

## Phase 13: 문서화 (30분)

### 13.1 README.md
- 프로젝트 소개
- 설치 방법
- 사용법
- 스크린샷

### 13.2 사용자 매뉴얼
- 기능 설명
- 트러블슈팅

### 13.3 코드 주석 정리
- Docstring 보완
- 주석 정리

### 체크리스트
- [ ] README.md 작성
- [ ] 사용자 매뉴얼 작성
- [ ] 코드 주석 검토
- [ ] API 문서 검토
- [ ] 최종 문서 검토

---

## 개발 환경 설정

### Python 환경
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 하드웨어 요구사항
- Zebra USB 프린터
- MCU 디바이스 (시리얼 포트)
- USB 케이블
- 라벨 용지

---

## 테스트 체크리스트

### 단위 테스트
- [ ] 데이터베이스 CRUD
- [ ] 시리얼 번호 생성
- [ ] PRN 파서
- [ ] MAC 파서
- [ ] 프린터 제어

### 통합 테스트
- [ ] CLI 전체 프로세스
- [ ] GUI 전체 프로세스
- [ ] 실제 하드웨어 연동

### 시나리오 테스트
- [ ] 신규 LOT 시작
- [ ] 연속 출력 (100개)
- [ ] LOT 변경
- [ ] 카운터 리셋
- [ ] 프린터 연결 끊김
- [ ] MCU 연결 끊김
- [ ] MAC 타임아웃
- [ ] DB 오류

---

## 우선순위

### P0 (필수)
- 데이터베이스 모듈
- 시리얼 번호 생성기
- PRN 파서
- 프린터 제어
- MCU 시리얼 통신
- 기본 GUI

### P1 (중요)
- 출력 이력
- 검색/필터
- 에러 핸들링
- 로깅

### P2 (선택)
- CSV 내보내기
- 백업 기능
- 통계 대시보드
- 다국어 지원

---

## 릴리스 계획

### v0.1.0 (CLI 버전)
- 핵심 백엔드 기능
- CLI 인터페이스
- 기본 테스트

### v0.2.0 (GUI 베타)
- PyQt6 GUI
- 기본 기능 구현

### v1.0.0 (정식 릴리스)
- 전체 기능 완성
- 안정화 및 최적화
- 사용자 매뉴얼

---

## 다음 단계

1. **Phase 1 시작**: 프로젝트 기본 설정
2. **백엔드 우선 개발**: Phase 2-7
3. **CLI 버전 완성 및 테스트**
4. **GUI 개발**: Phase 8-11
5. **통합 및 최종 테스트**: Phase 12-13
