"""
데이터베이스 관리자
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import (
    CREATE_TABLES,
    CREATE_INDEXES,
    CREATE_TRIGGERS,
    INSERT_INITIAL_DATA,
)
from .exceptions import (
    DatabaseError,
    DuplicateSerialNumberError,
    LOTConfigNotFoundError,
    ConfigKeyNotFoundError,
)


class DBManager:
    """SQLite 데이터베이스 관리자"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: SQLite DB 파일 경로
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """데이터베이스 연결"""
        if self.conn is not None:
            return

        # 디렉토리 생성
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # dict 형태로 결과 반환

    def initialize(self) -> None:
        """데이터베이스 초기화 (테이블, 인덱스, 트리거, 초기 데이터)"""
        self.connect()

        cursor = self.conn.cursor()

        # 테이블 생성
        cursor.executescript(CREATE_TABLES)

        # 인덱스 생성
        cursor.executescript(CREATE_INDEXES)

        # 트리거 생성
        cursor.executescript(CREATE_TRIGGERS)

        # 초기 데이터 삽입
        cursor.executescript(INSERT_INITIAL_DATA)

        self.conn.commit()

    def save_print_history(
        self,
        serial_number: str,
        mac_address: str,
        print_date: str,
        status: str,
        error_message: Optional[str] = None,
        prn_template: str = "PSA_LABEL_ZPL_with_mac_address.prn",
    ) -> int:
        """
        출력 이력 저장

        Args:
            serial_number: 시리얼 번호
            mac_address: MAC 주소
            print_date: 라벨에 표시된 날짜 (YYYY-MM-DD)
            status: 상태 ('success' or 'failed')
            error_message: 에러 메시지 (실패 시)
            prn_template: 사용한 PRN 템플릿 파일명

        Returns:
            삽입된 레코드 ID

        Raises:
            DuplicateSerialNumberError: 중복된 시리얼 번호
        """
        self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO print_history (
                    serial_number, mac_address, print_date, print_datetime,
                    status, error_message, prn_template
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    serial_number,
                    mac_address,
                    print_date,
                    datetime.now().isoformat(),
                    status,
                    error_message,
                    prn_template,
                ),
            )
            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateSerialNumberError(serial_number)
            raise DatabaseError(f"데이터베이스 오류: {e}")

    def get_print_history(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        serial_number: Optional[str] = None,
        mac_address: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        출력 이력 조회

        Args:
            limit: 조회 개수
            offset: 오프셋
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            serial_number: 시리얼 번호 (LIKE 검색)
            mac_address: MAC 주소 (LIKE 검색)

        Returns:
            이력 레코드 리스트
        """
        self.connect()

        query = "SELECT * FROM print_history WHERE 1=1"
        params = []

        if date_from:
            query += " AND DATE(print_datetime) >= ?"
            params.append(date_from)

        if date_to:
            query += " AND DATE(print_datetime) <= ?"
            params.append(date_to)

        if serial_number:
            query += " AND serial_number LIKE ?"
            params.append(f"%{serial_number}%")

        if mac_address:
            query += " AND mac_address LIKE ?"
            params.append(f"%{mac_address}%")

        query += " ORDER BY print_datetime DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def get_max_sequence_for_lot(self, lot_number: str) -> Optional[int]:
        """
        특정 LOT 번호의 최대 생산순서 조회

        Args:
            lot_number: LOT 번호 (예: "P10DL0S0H3A0C10")

        Returns:
            최대 생산순서 (예: 5) 또는 None (해당 LOT 기록 없음)
        """
        self.connect()

        cursor = self.conn.cursor()
        # 시리얼 번호에서 LOT 번호로 시작하는 모든 기록 찾기
        # 시리얼 형식: P10-DL0S0H3A0C100001-0
        # LOT 번호: P10DL0S0H3A0C10
        pattern = lot_number.replace('-', '')  # 하이픈 제거

        cursor.execute(
            """
            SELECT serial_number
            FROM print_history
            WHERE REPLACE(serial_number, '-', '') LIKE ?
            ORDER BY print_datetime DESC
            """,
            (f"{pattern}%",)
        )

        rows = cursor.fetchall()

        if not rows:
            return None

        # 모든 시리얼에서 생산순서 추출하여 최대값 찾기
        max_seq = 0
        for row in rows:
            serial = row['serial_number']
            # 시리얼에서 생산순서 추출: P10DL0S0H3A00C100011 → 0011
            # 형식: 20자리 고정, 마지막 4자리가 생산순서
            if len(serial) >= 20:
                seq_str = serial[-4:]  # 마지막 4자리
                try:
                    seq = int(seq_str)
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    continue

        return max_seq if max_seq > 0 else None

    def get_today_stats(self) -> Dict[str, int]:
        """
        오늘 출력 통계 조회

        Returns:
            {
                'total': 전체 출력 수,
                'success': 성공 수,
                'failed': 실패 수
            }
        """
        self.connect()

        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self.conn.cursor()

        # 오늘 날짜 기준 통계
        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM print_history
            WHERE DATE(print_datetime) = ?
            """,
            (today,)
        )

        row = cursor.fetchone()
        if row:
            return {
                'total': row['total'] or 0,
                'success': row['success'] or 0,
                'failed': row['failed'] or 0
            }

        return {'total': 0, 'success': 0, 'failed': 0}

    def get_lot_config(self) -> Dict[str, Any]:
        """
        LOT 설정 조회

        Returns:
            LOT 설정 dict

        Raises:
            LOTConfigNotFoundError: LOT 설정이 없음
        """
        self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM lot_config WHERE id = 1")
        row = cursor.fetchone()

        if row is None:
            raise LOTConfigNotFoundError()

        return dict(row)

    def update_lot_config(self, **kwargs) -> None:
        """
        LOT 설정 업데이트

        Args:
            model_code: 모델명 코드
            dev_code: 개발 코드
            robot_spec: 로봇 사양
            suite_spec: Suite 사양
            hw_code: HW 코드
            assembly_code: 조립 코드
            reserved: Reserved
            counter: 생산순서
        """
        self.connect()

        # 업데이트할 필드만 추출
        valid_fields = [
            "model_code",
            "dev_code",
            "robot_spec",
            "suite_spec",
            "hw_code",
            "assembly_code",
            "reserved",
            "production_date",
            "production_sequence",
        ]

        updates = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not updates:
            return

        # SQL 생성
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE lot_config SET {set_clause} WHERE id = 1"

        cursor = self.conn.cursor()
        cursor.execute(query, list(updates.values()))
        self.conn.commit()

    def increment_sequence(self, new_sequence: str) -> None:
        """
        생산순서 업데이트

        Args:
            new_sequence: 새 생산순서 값 (예: "0002")
        """
        self.update_lot_config(production_sequence=new_sequence)

    def get_config(self, key: str) -> Optional[str]:
        """
        앱 설정 조회

        Args:
            key: 설정 키

        Returns:
            설정 값 또는 None
        """
        self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
        row = cursor.fetchone()

        return row["value"] if row else None

    def set_config(self, key: str, value: str, description: str = "") -> None:
        """
        앱 설정 저장

        Args:
            key: 설정 키
            value: 설정 값
            description: 설명
        """
        self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO app_config (key, value, description)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?, description = ?
            """,
            (key, value, description, value, description),
        )
        self.conn.commit()

    def get_code_master(self, code_type: str) -> List[Dict[str, str]]:
        """
        코드 마스터 조회

        Args:
            code_type: 코드 타입 (model_code, dev_code 등)

        Returns:
            [{'code_value': 'P10', 'code_name': 'PSP 1.0'}, ...]
        """
        self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT code_value, code_name
            FROM code_master
            WHERE code_type = ? AND is_active = 1
            ORDER BY sort_order
            """,
            (code_type,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def backup(self, backup_path: str) -> None:
        """
        데이터베이스 백업

        Args:
            backup_path: 백업 파일 경로
        """
        if self.conn:
            self.conn.commit()

        # 백업 디렉토리 생성
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 파일 복사
        shutil.copy2(self.db_path, backup_path)

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()
