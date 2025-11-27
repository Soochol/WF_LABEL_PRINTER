"""이력 관리 서비스

인쇄 이력 조회, 검색, 삭제를 담당합니다.
"""

from typing import Optional


class HistoryService:
    """이력 관리 서비스"""

    def __init__(self, db):
        """
        Args:
            db: DBManager 인스턴스
        """
        self.db = db

    def get_all(self, limit: int = 1000) -> list:
        """전체 이력 조회

        Args:
            limit: 최대 조회 개수

        Returns:
            이력 목록
        """
        return self.db.get_print_history(limit=limit)

    def search(self, filters: dict) -> list:
        """이력 검색

        Args:
            filters: 검색 필터
                - date_from: 시작 날짜
                - date_to: 종료 날짜
                - serial_number: 시리얼 번호 (부분 일치)
                - mac_address: MAC 주소 (부분 일치)

        Returns:
            검색 결과 목록
        """
        return self.db.get_print_history(
            limit=1000,
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to'),
            serial_number=filters.get('serial_number'),
            mac_address=filters.get('mac_address')
        )

    def delete(self, record_id: int) -> bool:
        """이력 삭제 및 생산순서 업데이트

        Args:
            record_id: 삭제할 레코드 ID

        Returns:
            삭제 성공 여부
        """
        # DB에서 삭제
        if not self.db.delete_print_history(record_id):
            return False

        # 최신 기록으로 생산순서 업데이트
        self._update_production_sequence()

        return True

    def _update_production_sequence(self) -> None:
        """최신 이력 기반으로 생산순서 업데이트"""
        latest = self.db.get_print_history(limit=1)

        if latest:
            # 시리얼 번호에서 마지막 4자리 (생산순서) 추출
            # 시리얼 형식: P10-DL0S0H3A0C100001-0
            serial_number = latest[0]['serial_number']
            parts = serial_number.split('-')
            if len(parts) >= 2:
                lot_with_seq = parts[1]
                sequence = lot_with_seq[-4:]
                self.db.update_lot_config(production_sequence=sequence)
        else:
            # 이력이 없으면 0001로 초기화
            self.db.update_lot_config(production_sequence="0001")

    def get_by_date_range(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000
    ) -> list:
        """날짜 범위로 이력 조회

        Args:
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            limit: 최대 조회 개수

        Returns:
            이력 목록
        """
        return self.db.get_print_history(
            limit=limit,
            date_from=date_from,
            date_to=date_to
        )
