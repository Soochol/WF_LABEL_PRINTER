"""
Zebra Label Printer - CLI Test Version
전체 워크플로우 통합 테스트
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DBManager
from src.printer.zebra_win_controller import ZebraWinController
from src.printer.prn_parser import PRNParser
# MCUMonitor는 필요할 때만 import (PyQt6 의존성)
# from src.serial_comm.mcu_monitor import MCUMonitor
from src.serial_comm.mac_parser import MACParser
from src.utils.serial_number_generator import SerialNumberGenerator
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger


def main():
    """메인 CLI 애플리케이션"""

    # 로거 설정
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("Zebra Label Printer - CLI Test Version")
    logger.info("=" * 60)

    try:
        # 1. 설정 로드
        logger.info("\n[1/8] 설정 파일 로드 중...")
        config = ConfigManager("config.yaml")
        logger.info("✓ 설정 파일 로드 완료")

        # 2. 데이터베이스 초기화
        logger.info("\n[2/8] 데이터베이스 초기화 중...")
        db_path = config.get("database.path", "data/label_printer.db")
        db = DBManager(db_path)
        db.initialize()
        logger.info(f"✓ 데이터베이스 초기화 완료: {db_path}")

        # 3. LOT 설정 로드
        logger.info("\n[3/8] LOT 설정 로드 중...")
        lot_config = db.get_lot_config()
        logger.info(f"✓ LOT 설정: {lot_config}")

        # 4. 시리얼 번호 생성기 초기화
        logger.info("\n[4/8] 시리얼 번호 생성기 초기화 중...")
        # DB 필드 중 SerialNumberGenerator에 필요한 것만 추출
        sn_params = {k: v for k, v in lot_config.items() if k in [
            'model_code', 'dev_code', 'robot_spec', 'suite_spec',
            'hw_code', 'assembly_code', 'reserved', 'production_date', 'production_sequence'
        ]}
        sn_gen = SerialNumberGenerator(**sn_params)
        current_serial = sn_gen.generate()
        logger.info(f"✓ 현재 시리얼 번호: {current_serial}")
        logger.info(f"  - LOT 코드: {sn_gen.get_lot_code()}")
        logger.info(f"  - 생산일자: {sn_gen.production_date}")
        logger.info(f"  - 생산순서: {sn_gen.production_sequence}")

        # 5. PRN 템플릿 로드
        logger.info("\n[5/8] PRN 템플릿 로드 중...")
        template_path = config.get("printer.default_template", "templates/PSA_LABEL_ZPL_with_mac_address.prn")
        parser = PRNParser(template_path)
        logger.info(f"✓ PRN 템플릿 로드 완료: {template_path}")

        if not parser.has_all_variables():
            missing = parser.get_missing_variables()
            logger.warning(f"⚠ 누락된 변수: {missing}")

        # 6. 프린터 검색
        logger.info("\n[6/8] Zebra 프린터 검색 중...")
        printer_controller = ZebraWinController()
        printers = printer_controller.get_zebra_printers()

        if not printers:
            logger.warning("⚠ Zebra 프린터를 찾을 수 없습니다.")
            logger.info("  테스트 모드로 계속 진행합니다.")
            printer_connected = False
        else:
            logger.info(f"✓ {len(printers)}개의 Zebra 프린터 발견:")
            for i, p in enumerate(printers):
                logger.info(f"  [{i+1}] {p}")

            printer_connected = True

        # 7. MCU 시리얼 통신 (시뮬레이션)
        logger.info("\n[7/8] MCU 시리얼 통신 테스트...")
        serial_port = config.get("serial.port", "COM3")
        logger.info(f"  시리얼 포트: {serial_port}")

        # 실제 MCU 연결 시도는 하드웨어가 있을 때만
        logger.info("  테스트 모드: MAC 주소 시뮬레이션")
        test_mac = "PSAD0CF1327829495"
        logger.info(f"✓ 테스트 MAC 주소: {test_mac}")

        # 8. 라벨 출력 시뮬레이션
        logger.info("\n[8/8] 라벨 출력 시뮬레이션...")

        # 현재 날짜
        current_date = datetime.now().strftime("%Y.%m.%d")

        # 변수 치환
        logger.info("  변수 치환 중...")
        zpl_commands = parser.replace_variables(
            date=current_date,
            serial_number=current_serial,
            mac_address=test_mac,
        )
        logger.info(f"✓ ZPL 명령 생성 완료 (길이: {len(zpl_commands)} bytes)")

        # 프린터 출력 (실제 프린터가 있을 경우)
        if printer_connected:
            try:
                logger.info("  프린터 연결 중...")
                printer_controller.connect()
                logger.info(f"✓ 프린터 연결 성공: {printer_controller.queue_name}")

                logger.info("  라벨 출력 중...")
                printer_controller.send_zpl(zpl_commands)
                logger.info("✓ 라벨 출력 완료")

                print_status = "success"

            except Exception as e:
                logger.error(f"✗ 프린터 오류: {e}")
                print_status = "failed"
        else:
            logger.info("  테스트 모드: 실제 출력 건너뛰기")
            print_status = "success"

        # 9. 데이터베이스에 이력 저장
        logger.info("\n[9/9] 출력 이력 저장 중...")
        try:
            record_id = db.save_print_history(
                serial_number=current_serial,
                mac_address=test_mac,
                print_date=datetime.now().strftime("%Y-%m-%d"),
                status=print_status,
                prn_template=Path(template_path).name,
            )
            logger.info(f"✓ 출력 이력 저장 완료 (ID: {record_id})")
        except Exception as e:
            logger.error(f"✗ 이력 저장 실패: {e}")

        # 10. 생산순서 증가
        logger.info("\n[10/10] 생산순서 증가 중...")
        sn_gen.increment_sequence()
        new_sequence = sn_gen.production_sequence
        db.increment_sequence(new_sequence)
        logger.info(f"✓ 생산순서 업데이트: {new_sequence}")

        # 11. 최근 출력 이력 조회
        logger.info("\n=== 최근 출력 이력 (최근 5개) ===")
        history = db.get_print_history(limit=5)
        for record in history:
            logger.info(f"  [{record['id']}] {record['serial_number']} | {record['mac_address']} | {record['status']}")

        # 완료
        logger.info("\n" + "=" * 60)
        logger.info("✓ 전체 프로세스 완료!")
        logger.info("=" * 60)

        # 데이터베이스 종료
        db.close()

        return 0

    except KeyboardInterrupt:
        logger.info("\n\n사용자에 의해 중단되었습니다.")
        return 1

    except Exception as e:
        logger.error(f"\n✗ 오류 발생: {e}", exc_info=True)
        return 1


def test_serial_number_generator():
    """시리얼 번호 생성기 단독 테스트"""
    print("\n=== Serial Number Generator Test ===")

    gen = SerialNumberGenerator()

    for i in range(5):
        sn = gen.generate()
        print(f"{i+1}. {sn}")
        gen.increment_sequence()

    print(f"\nLOT Code: {gen.get_lot_code()}")
    print(f"Production Date: {gen.production_date}")
    print(f"Production Sequence: {gen.production_sequence}")


def test_prn_parser():
    """PRN 파서 단독 테스트"""
    print("\n=== PRN Parser Test ===")

    parser = PRNParser("templates/PSA_LABEL_ZPL_with_mac_address.prn")

    zpl = parser.replace_variables(
        date="2025.10.17",
        serial_number="P10DL0S0H3A00C100001",
        mac_address="PSAD0CF1327829495",
    )

    print(f"ZPL Length: {len(zpl)} bytes")
    print(f"Has all variables: {parser.has_all_variables()}")
    print(f"\nFirst 500 chars:\n{zpl[:500]}")


def test_database():
    """데이터베이스 단독 테스트"""
    print("\n=== Database Test ===")

    db = DBManager(":memory:")
    db.initialize()

    # LOT 설정 조회
    lot_config = db.get_lot_config()
    print(f"LOT Config: {lot_config}")

    # 출력 이력 저장
    db.save_print_history(
        serial_number="P10DL0S0H3A00C100001",
        mac_address="TEST123",
        print_date="2025-10-17",
        status="success",
    )

    # 이력 조회
    history = db.get_print_history(limit=10)
    print(f"\nPrint History: {len(history)} records")
    for record in history:
        print(f"  {record['serial_number']} | {record['status']}")

    db.close()


if __name__ == "__main__":
    import argparse

    parser_cli = argparse.ArgumentParser(description="Zebra Label Printer CLI")
    parser_cli.add_argument(
        "--test",
        choices=["serial", "prn", "db", "all"],
        help="Run specific test module",
    )

    args = parser_cli.parse_args()

    if args.test == "serial":
        test_serial_number_generator()
    elif args.test == "prn":
        test_prn_parser()
    elif args.test == "db":
        test_database()
    elif args.test == "all":
        test_serial_number_generator()
        test_prn_parser()
        test_database()
    else:
        # 메인 애플리케이션 실행
        sys.exit(main())
