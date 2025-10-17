# WF Label Printer - 배포 가이드

## 빌드 방법

### 1. 사전 요구사항
- Python 3.10 이상
- PyInstaller
- 프로젝트의 모든 의존성 패키지

### 2. 빌드 실행

#### Windows에서 빌드
```bash
# 간단한 방법: build.bat 실행
build.bat
```

또는 수동으로:
```bash
# 1. PyInstaller 설치
pip install pyinstaller

# 2. 빌드 실행
pyinstaller WF_Label_Printer.spec --clean
```

### 3. 빌드 결과
- **위치**: `build/WF_Label_Printer/`
- **실행 파일**: `build/WF_Label_Printer/WF_Label_Printer.exe`

## 배포 패키지 구조

```
build/WF_Label_Printer/
├── WF_Label_Printer.exe    # 실행 파일
├── templates/               # PRN 템플릿 파일
│   └── PSA_LABEL_ZPL_with_mac_address.prn
├── data/                    # 데이터베이스 저장 폴더 (자동 생성)
│   └── label_printer.db    # 최초 실행 시 생성
├── _internal/              # PyInstaller 내부 파일들
├── README.md               # 프로젝트 설명
└── PRINTER_SETUP.md        # 프린터 설정 가이드
```

## 배포 방법

### 1. 폴더 전체 복사
`build/WF_Label_Printer/` 폴더 전체를 대상 PC에 복사합니다.

### 2. 필수 사전 준비 (대상 PC)
1. **Zebra USB 프린터 드라이버 설치**
   - Zebra 공식 사이트에서 드라이버 다운로드
   - 프린터를 USB로 연결하여 드라이버 설치

2. **libusb 설치** (USB 통신용)
   - 다운로드: https://github.com/libusb/libusb/releases
   - `libusb-1.0.dll` 파일을 시스템 경로에 복사
   - 또는 실행 파일과 같은 폴더에 복사

3. **MCU 시리얼 포트 확인**
   - 장치 관리자에서 COM 포트 번호 확인
   - 프로그램 실행 후 설정 페이지에서 포트 설정

### 3. 실행
`WF_Label_Printer.exe`를 더블클릭하여 실행합니다.

## 최초 실행 시 설정

### 1. 데이터베이스 자동 생성
- 최초 실행 시 `data/label_printer.db` 파일이 자동 생성됩니다
- 초기 LOT 설정, 코드 마스터 데이터가 자동으로 입력됩니다

### 2. 프린터 설정 확인
1. **설정** 메뉴로 이동
2. **Zebra 프린터 설정** 확인
   - VID: 0x0A5F (Zebra 기본값)
   - PID: 빈 값 (자동 검색)
3. **MCU 시리얼 포트 설정**
   - COM 포트 번호 입력 (예: COM3)
   - 보드레이트: 115200

### 3. LOT 설정
1. **LOT 설정** 메뉴로 이동
2. 제품 정보 입력:
   - 모델명 코드
   - 개발 코드
   - 로봇 사양 코드
   - Suite 사양 코드
   - HW 코드
   - 조립 코드
   - 생산일자 코드
3. 설정은 자동 저장됩니다 (500ms 딜레이)

## 문제 해결

### 프린터가 인식되지 않을 때
1. Zebra 드라이버가 설치되었는지 확인
2. libusb-1.0.dll 파일이 있는지 확인
3. USB 케이블 재연결
4. 프로그램 재시작

### MCU가 연결되지 않을 때
1. 장치 관리자에서 COM 포트 번호 확인
2. 설정에서 올바른 포트 번호 입력
3. USB 케이블 재연결
4. 프로그램 재시작

### 데이터베이스 오류 발생 시
1. `data/label_printer.db` 파일 삭제
2. 프로그램 재시작 (자동으로 새 DB 생성)
3. LOT 설정 다시 입력

## 업데이트 방법

### 1. 기존 데이터 백업
```
data/label_printer.db -> 다른 위치에 백업
```

### 2. 프로그램 폴더 교체
- 기존 `WF_Label_Printer` 폴더 삭제
- 새 버전의 `WF_Label_Printer` 폴더 복사

### 3. 데이터 복원
```
백업한 label_printer.db -> data/label_printer.db로 복사
```

## 시스템 요구사항

### 최소 사양
- **OS**: Windows 10 이상 (64-bit)
- **RAM**: 4GB 이상
- **디스크**: 500MB 여유 공간
- **USB**: USB 2.0 이상 포트

### 권장 사양
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8GB 이상
- **디스크**: 1GB 여유 공간
- **USB**: USB 3.0 포트

## 라이선스 및 의존성

### 주요 의존성 패키지
- PyQt6 6.6.1 - GUI 프레임워크
- pyusb 1.2.1 - USB 프린터 통신
- pyserial 3.5 - MCU 시리얼 통신
- sqlite3 - 데이터베이스 (Python 내장)

### 라이선스
프로젝트 라이선스 정보는 LICENSE 파일을 참조하세요.

## 지원

문제 발생 시:
1. `data/label_printer.db` 파일 확인
2. 프로그램 로그 확인 (콘솔 출력)
3. PRINTER_SETUP.md 참조
4. 개발팀 문의
