"""
하드웨어 연결 상태 확인 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("하드웨어 연결 상태 확인")
print("=" * 60)

# 1. Python 버전 확인
print(f"\n✓ Python 버전: {sys.version}")

# 2. 필수 라이브러리 확인
print("\n필수 라이브러리 확인:")
required_modules = [
    ("usb.core", "pyusb"),
    ("serial", "pyserial"),
    ("yaml", "pyyaml"),
    ("PyQt6", "PyQt6"),
]

missing_modules = []
for module_name, package_name in required_modules:
    try:
        __import__(module_name)
        print(f"  ✓ {package_name}")
    except ImportError:
        print(f"  ✗ {package_name} - 설치 필요: pip install {package_name}")
        missing_modules.append(package_name)

if missing_modules:
    print(f"\n⚠ 누락된 라이브러리가 있습니다. 다음 명령으로 설치하세요:")
    print(f"   pip install {' '.join(missing_modules)}")
    sys.exit(1)

# 3. Zebra 프린터 검색
print("\n\nZebra 프린터 검색 중...")
try:
    from src.printer.printer_discovery import PrinterDiscovery

    printers = PrinterDiscovery.find_zebra_printers()

    if printers:
        print(f"✓ {len(printers)}개의 Zebra 프린터 발견:")
        for i, printer in enumerate(printers):
            print(f"\n  [{i+1}] {printer.get('manufacturer', 'Unknown')} {printer.get('product', 'Unknown')}")
            print(f"      VID: 0x{printer['vendor_id']:04X}")
            print(f"      PID: 0x{printer['product_id']:04X}")
            print(f"      Bus: {printer.get('bus', 'N/A')}, Address: {printer.get('address', 'N/A')}")
            if 'serial' in printer and printer['serial']:
                print(f"      Serial: {printer['serial']}")
    else:
        print("⚠ Zebra 프린터를 찾을 수 없습니다.")
        print("\n확인 사항:")
        print("  1. USB 케이블이 연결되어 있는지 확인")
        print("  2. 프린터 전원이 켜져 있는지 확인")
        print("  3. Windows의 경우 Zadig로 드라이버 설치 확인")
        print("     (https://zadig.akeo.ie/)")

except Exception as e:
    print(f"✗ 프린터 검색 오류: {e}")
    print("\n권한 문제일 수 있습니다:")
    print("  - Windows: 관리자 권한으로 실행")
    print("  - Linux: sudo 권한 또는 udev 규칙 설정")

# 4. 시리얼 포트 확인
print("\n\n시리얼 포트 확인 중...")
try:
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    if ports:
        print(f"✓ {len(ports)}개의 시리얼 포트 발견:")
        for port in ports:
            print(f"\n  {port.device}")
            print(f"    설명: {port.description}")
            if port.manufacturer:
                print(f"    제조사: {port.manufacturer}")
            if port.hwid:
                print(f"    HW ID: {port.hwid}")
    else:
        print("⚠ 시리얼 포트를 찾을 수 없습니다.")
        print("  MCU가 연결되어 있는지 확인하세요.")

except Exception as e:
    print(f"✗ 시리얼 포트 검색 오류: {e}")

# 5. 데이터베이스 확인
print("\n\n데이터베이스 확인 중...")
try:
    from src.database.db_manager import DBManager

    db = DBManager(":memory:")  # 테스트용 인메모리 DB
    db.initialize()

    lot_config = db.get_lot_config()
    print(f"✓ 데이터베이스 초기화 성공")
    print(f"  LOT 설정: {lot_config.get('model_code', '')}{lot_config.get('dev_code', '')}")

    db.close()

except Exception as e:
    print(f"✗ 데이터베이스 오류: {e}")

# 6. PRN 템플릿 확인
print("\n\nPRN 템플릿 확인 중...")
try:
    prn_path = Path("templates/PSA_LABEL_ZPL_with_mac_address.prn")

    if prn_path.exists():
        print(f"✓ PRN 템플릿 파일 존재: {prn_path}")
        print(f"  파일 크기: {prn_path.stat().st_size} bytes")

        from src.printer.prn_parser import PRNParser
        parser = PRNParser(str(prn_path))

        if parser.has_all_variables():
            print(f"  ✓ 모든 필수 변수 포함됨")
        else:
            missing = parser.get_missing_variables()
            print(f"  ⚠ 누락된 변수: {missing}")
    else:
        print(f"✗ PRN 템플릿 파일이 없습니다: {prn_path}")

except Exception as e:
    print(f"✗ PRN 템플릿 오류: {e}")

# 7. 시리얼 번호 생성기 테스트
print("\n\n시리얼 번호 생성기 테스트...")
try:
    from src.utils.serial_number_generator import SerialNumberGenerator

    gen = SerialNumberGenerator()
    test_serial = gen.generate()

    print(f"✓ 시리얼 번호 생성 성공")
    print(f"  생성된 번호: {test_serial}")
    print(f"  LOT 코드: {gen.get_lot_code()}")
    print(f"  생산일자: {gen.production_date}")
    print(f"  생산순서: {gen.production_sequence}")

    # 검증
    if SerialNumberGenerator.validate(test_serial):
        print(f"  ✓ 형식 검증 통과")
    else:
        print(f"  ✗ 형식 검증 실패")

except Exception as e:
    print(f"✗ 시리얼 번호 생성기 오류: {e}")

# 최종 결과
print("\n" + "=" * 60)
print("하드웨어 확인 완료")
print("=" * 60)

if not printers:
    print("\n⚠ 주의: Zebra 프린터가 연결되지 않았습니다.")
    print("   테스트 모드로만 실행 가능합니다.")
else:
    print("\n✓ 모든 하드웨어가 준비되었습니다!")
    print("   다음 명령으로 전체 프로세스를 테스트하세요:")
    print("   python src/main.py")
