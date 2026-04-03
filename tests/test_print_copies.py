"""
인쇄 매수 (Print Copies) 기능 테스트

^PQ 명령어 주입 로직을 검증합니다.
"""

import sys
from unittest.mock import MagicMock

# zebra 라이브러리 mock (Windows 전용 프린터 드라이버)
sys.modules['zebra'] = MagicMock()

import pytest
from src.printer.print_controller import PrintController


@pytest.fixture
def controller():
    """PrintController 인스턴스"""
    return PrintController()


class TestInjectPrintQuantity:
    """_inject_print_quantity() 메서드 테스트"""

    def test_replaces_existing_pq(self, controller):
        """기존 ^PQ 명령이 있으면 교체"""
        zpl = "^XA\n^FT100,100^FDTEST^FS\n^PQ1,,,Y\n^XZ"
        result = controller._inject_print_quantity(zpl, 3)
        assert "^PQ3,,,Y" in result
        assert "^PQ1,,,Y" not in result

    def test_inserts_when_no_pq(self, controller):
        """^PQ 명령이 없으면 마지막 ^XZ 앞에 삽입"""
        zpl = "^XA\n^FT100,100^FDTEST^FS\n^XZ"
        result = controller._inject_print_quantity(zpl, 2)
        assert "^PQ2,,,Y" in result
        assert result.endswith("^XZ")

    def test_default_copies_1(self, controller):
        """copies=1일 때 ^PQ1,,,Y"""
        zpl = "^XA\n^FT100,100^FDTEST^FS\n^XZ"
        result = controller._inject_print_quantity(zpl, 1)
        assert "^PQ1,,,Y" in result

    def test_inserts_before_last_xz_in_multi_block(self, controller):
        """여러 ^XA/^XZ 블록이 있을 때 마지막 ^XZ 앞에 삽입"""
        zpl = "^XA\n^XZ\n^XA\n^FT100,100^FDLABEL^FS\n^XZ"
        result = controller._inject_print_quantity(zpl, 4)
        # 마지막 ^XZ 앞에만 삽입
        assert result.count("^PQ4,,,Y") == 1
        assert result.endswith("^XZ")

    def test_replaces_pq_with_different_format(self, controller):
        """^PQ 뒤에 다른 파라미터가 있어도 교체"""
        zpl = "^XA\n^PQ1,0,0,Y\n^XZ"
        result = controller._inject_print_quantity(zpl, 5)
        assert "^PQ5,,,Y" in result
        assert "^PQ1" not in result

    def test_no_xz_returns_unchanged(self, controller):
        """^XZ가 없는 비정상 ZPL은 그대로 반환"""
        zpl = "^XA\n^FDTEST^FS"
        result = controller._inject_print_quantity(zpl, 3)
        assert result == zpl


class TestTestZplPrintQuantity:
    """테스트 ZPL에 인쇄 매수 적용"""

    def test_test_zpl_has_pq_replaced(self, controller):
        """_get_test_zpl_data()의 ^PQ1이 지정 매수로 교체됨"""
        zpl = controller._get_test_zpl_data()
        result = controller._inject_print_quantity(zpl, 3)
        assert "^PQ3,,,Y" in result
        assert "^PQ1,,,Y" not in result
