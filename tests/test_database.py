"""
데이터베이스 모듈 테스트
"""

import pytest
import os
from datetime import datetime
from src.database.db_manager import DBManager
from src.database.exceptions import (
    DuplicateSerialNumberError,
    LOTConfigNotFoundError,
)


@pytest.fixture
def db():
    """테스트용 인메모리 데이터베이스"""
    db = DBManager(":memory:")
    db.initialize()
    yield db
    db.close()


def test_db_initialization(db):
    """데이터베이스 초기화 테스트"""
    # LOT 설정이 초기화되었는지 확인
    lot_config = db.get_lot_config()
    assert lot_config is not None
    assert lot_config["model_code"] == "P10"
    assert lot_config["counter"] == "A00"


def test_save_print_history(db):
    """출력 이력 저장 테스트"""
    record_id = db.save_print_history(
        serial_number="P10DL0S0H3A00A01",
        mac_address="PSAD0CF1327829495",
        print_date="2025-10-17",
        status="success",
    )

    assert record_id > 0

    # 조회 확인
    history = db.get_print_history(limit=1)
    assert len(history) == 1
    assert history[0]["serial_number"] == "P10DL0S0H3A00A01"
    assert history[0]["mac_address"] == "PSAD0CF1327829495"


def test_duplicate_serial_number(db):
    """중복 시리얼 번호 테스트"""
    db.save_print_history(
        serial_number="P10DL0S0H3A00A01",
        mac_address="PSAD0CF1327829495",
        print_date="2025-10-17",
        status="success",
    )

    # 같은 시리얼 번호로 다시 저장 시도
    with pytest.raises(DuplicateSerialNumberError):
        db.save_print_history(
            serial_number="P10DL0S0H3A00A01",
            mac_address="PSAD0CF1327829496",
            print_date="2025-10-17",
            status="success",
        )


def test_get_print_history_with_filters(db):
    """필터를 사용한 출력 이력 조회 테스트"""
    # 여러 개 데이터 삽입
    db.save_print_history(
        "P10DL0S0H3A00A01", "MAC001", "2025-10-17", "success"
    )
    db.save_print_history(
        "P10DL0S0H3A00A02", "MAC002", "2025-10-17", "success"
    )
    db.save_print_history(
        "P10DL0S0H3A00A03", "MAC003", "2025-10-18", "failed"
    )

    # 날짜 필터
    history = db.get_print_history(date_from="2025-10-17", date_to="2025-10-17")
    assert len(history) == 2

    # 시리얼 번호 필터
    history = db.get_print_history(serial_number="A02")
    assert len(history) == 1
    assert history[0]["serial_number"] == "P10DL0S0H3A00A02"

    # 상태 필터
    history = db.get_print_history(status="failed")
    assert len(history) == 1


def test_update_lot_config(db):
    """LOT 설정 업데이트 테스트"""
    db.update_lot_config(
        model_code="W10",
        counter="B05",
    )

    lot_config = db.get_lot_config()
    assert lot_config["model_code"] == "W10"
    assert lot_config["counter"] == "B05"
    # 다른 필드는 유지
    assert lot_config["dev_code"] == "D"


def test_increment_counter(db):
    """카운터 증가 테스트"""
    db.increment_counter("B04")

    lot_config = db.get_lot_config()
    assert lot_config["counter"] == "B04"


def test_app_config(db):
    """앱 설정 테스트"""
    # 초기 설정 조회
    port = db.get_config("serial_port")
    assert port == "COM3"

    # 설정 변경
    db.set_config("serial_port", "COM5", "Updated port")
    port = db.get_config("serial_port")
    assert port == "COM5"

    # 없는 키 조회
    value = db.get_config("non_existent_key")
    assert value is None


def test_get_code_master(db):
    """코드 마스터 조회 테스트"""
    # 모델명 코드 조회
    model_codes = db.get_code_master("model_code")
    assert len(model_codes) == 4
    assert model_codes[0]["code_value"] == "P10"
    assert model_codes[0]["code_name"] == "PSP 1.0"

    # 개발 코드 조회
    dev_codes = db.get_code_master("dev_code")
    assert len(dev_codes) == 5


def test_backup(db, tmp_path):
    """백업 테스트"""
    # 실제 파일 DB 생성
    db_path = tmp_path / "test.db"
    db_test = DBManager(str(db_path))
    db_test.initialize()

    # 데이터 삽입
    db_test.save_print_history(
        "P10DL0S0H3A00A01", "MAC001", "2025-10-17", "success"
    )

    # 백업
    backup_path = tmp_path / "backups" / "test_backup.db"
    db_test.backup(str(backup_path))

    assert backup_path.exists()

    # 백업 파일 검증
    db_backup = DBManager(str(backup_path))
    db_backup.connect()
    history = db_backup.get_print_history()
    assert len(history) == 1

    db_test.close()
    db_backup.close()


def test_context_manager():
    """Context manager 테스트"""
    with DBManager(":memory:") as db:
        db.initialize()
        lot_config = db.get_lot_config()
        assert lot_config is not None

    # with 블록을 벗어나면 자동으로 close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
