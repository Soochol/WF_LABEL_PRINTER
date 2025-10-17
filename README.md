# Zebra Label Printer Control System

WITHFORCE INC. - 시리얼 번호 라벨 자동 출력 시스템

## 📋 개요

Zebra USB 프린터를 제어하여 제품 시리얼 번호가 포함된 라벨을 자동으로 출력하는 시스템입니다.

## 🔢 시리얼 번호 구조 (20자리)

```
P10DL0S0H3A00C100001
└─ 모델명(3) + 개발(1) + 로봇(2) + Suite(2) + HW(2) + 조립(2) + Reserved(1) + 생산일자(3) + 생산순서(4)
```

**생산일자 코드:** A=2023년, B=2024년, C=2025년 + 월(2자리)
**예시:** C10 = 2025년 10월

## 🚀 CLI 테스트

```bash
python src/main.py                    # 전체 프로세스
python src/main.py --test serial      # 시리얼 번호 테스트
python src/main.py --test prn         # PRN 파서 테스트
python src/main.py --test db          # 데이터베이스 테스트
```

## 📁 주요 파일

- `src/main.py` - CLI 테스트 버전
- `src/utils/serial_number_generator.py` - 시리얼 번호 생성기
- `src/printer/prn_parser.py` - PRN 파일 파서
- `src/database/db_manager.py` - 데이터베이스 관리자
- `docs/` - 상세 설계 문서

## 📞 문의

WITHFORCE INC. - A/S: 031-426-2301
