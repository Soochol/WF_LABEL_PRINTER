# 데이터베이스 스키마

## 개요
- **DBMS**: SQLite 3
- **파일 위치**: `./data/label_printer.db`
- **문자 인코딩**: UTF-8
- **백업**: 자동 백업 (1시간마다)

## 테이블 구조

### 1. print_history (출력 이력)

#### 목적
라벨 출력 이력을 기록하여 추적 가능성 제공

#### 스키마
```sql
CREATE TABLE print_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL,           -- 출력한 시리얼 번호
    mac_address TEXT NOT NULL,             -- MAC 주소 (device id)
    print_date DATE NOT NULL,              -- 라벨에 표시된 날짜 (YYYY-MM-DD)
    print_datetime DATETIME NOT NULL,      -- 실제 출력 시각
    status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
    error_message TEXT,                    -- 실패 시 에러 메시지
    prn_template TEXT NOT NULL,            -- 사용한 PRN 템플릿 파일명
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(serial_number)                  -- 시리얼 번호 중복 방지
);
```

#### 인덱스
```sql
CREATE INDEX idx_print_history_date ON print_history(print_datetime DESC);
CREATE INDEX idx_print_history_serial ON print_history(serial_number);
CREATE INDEX idx_print_history_mac ON print_history(mac_address);
CREATE INDEX idx_print_history_status ON print_history(status);
```

#### 예시 데이터
```sql
INSERT INTO print_history (
    serial_number,
    mac_address,
    print_date,
    print_datetime,
    status,
    prn_template
) VALUES (
    'P10DL0S0H3A00B03',
    'PSAD0CF1327829495',
    '2025-10-17',
    '2025-10-17 10:53:42',
    'success',
    'PSA_LABEL_ZPL_with_mac_address.prn'
);
```

---

### 2. lot_config (LOT 설정)

#### 목적
현재 LOT 정보 및 생산순서 카운터 저장

#### 스키마
```sql
CREATE TABLE lot_config (
    id INTEGER PRIMARY KEY CHECK(id = 1),  -- 단일 레코드만 허용
    model_code TEXT NOT NULL,              -- 모델명 코드 (P10)
    dev_code TEXT NOT NULL,                -- 개발 코드 (D)
    robot_spec TEXT NOT NULL,              -- 로봇 사양 (L0)
    suite_spec TEXT NOT NULL,              -- Suite 사양 (S0)
    hw_code TEXT NOT NULL,                 -- HW 코드 (H3)
    assembly_code TEXT NOT NULL,           -- 조립 코드 (A0)
    reserved TEXT NOT NULL DEFAULT '0',    -- Reserved (0)
    counter TEXT NOT NULL,                 -- 생산순서 (B03)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 트리거 (자동 업데이트)
```sql
CREATE TRIGGER update_lot_config_timestamp
AFTER UPDATE ON lot_config
BEGIN
    UPDATE lot_config SET updated_at = CURRENT_TIMESTAMP WHERE id = 1;
END;
```

#### 초기 데이터
```sql
INSERT INTO lot_config (
    id, model_code, dev_code, robot_spec, suite_spec,
    hw_code, assembly_code, reserved, counter
) VALUES (
    1, 'P10', 'D', 'L0', 'S0', 'H3', 'A0', '0', 'A00'
);
```

---

### 3. app_config (애플리케이션 설정)

#### 목적
앱 설정 Key-Value 저장

#### 스키마
```sql
CREATE TABLE app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 트리거 (자동 업데이트)
```sql
CREATE TRIGGER update_app_config_timestamp
AFTER UPDATE ON app_config
BEGIN
    UPDATE app_config SET updated_at = CURRENT_TIMESTAMP
    WHERE key = NEW.key;
END;
```

#### 초기 데이터
```sql
INSERT INTO app_config (key, value, description) VALUES
    ('printer_vendor_id', '0x0A5F', 'Zebra 프린터 VID'),
    ('printer_product_id', '', '프린터 PID (빈값=자동검색)'),
    ('serial_port', 'COM3', 'MCU 시리얼 포트'),
    ('serial_baudrate', '115200', 'MCU 보드레이트'),
    ('serial_timeout', '30', 'MAC 수신 타임아웃 (초)'),
    ('prn_template', 'PSA_LABEL_ZPL_with_mac_address.prn', '기본 PRN 템플릿'),
    ('auto_increment', 'true', '생산순서 자동 증가 활성화'),
    ('backup_enabled', 'true', 'DB 백업 활성화'),
    ('backup_interval', '3600', '백업 주기 (초)'),
    ('last_backup', '', '마지막 백업 시각');
```

---

### 4. code_master (코드 마스터)

#### 목적
드롭다운 메뉴에 사용될 코드 값 관리

#### 스키마
```sql
CREATE TABLE code_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_type TEXT NOT NULL,               -- 코드 타입
    code_value TEXT NOT NULL,              -- 코드 값
    code_name TEXT NOT NULL,               -- 코드 이름 (한글)
    sort_order INTEGER DEFAULT 0,          -- 정렬 순서
    is_active BOOLEAN DEFAULT 1,           -- 활성화 여부
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(code_type, code_value)
);
```

#### 인덱스
```sql
CREATE INDEX idx_code_master_type ON code_master(code_type, sort_order);
```

#### 초기 데이터
```sql
-- 모델명 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('model_code', 'P10', 'PSP 1.0', 1),
    ('model_code', 'W10', 'WSP 1.0', 2),
    ('model_code', 'M10', 'M10', 3),
    ('model_code', 'A10', 'PSA 1.0', 4);

-- 개발 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('dev_code', 'P', 'Pilot', 1),
    ('dev_code', 'M', 'Manufacturing(양산)', 2),
    ('dev_code', 'T', 'Test', 3),
    ('dev_code', 'D', 'Demo(시연)', 4),
    ('dev_code', 'R', 'Replacement(교체품)', 5);

-- 로봇 사양 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('robot_spec', 'L0', 'L230-A39', 1),
    ('robot_spec', 'L1', 'L210-A39', 2),
    ('robot_spec', 'L2', 'L220-A39', 3),
    ('robot_spec', 'L3', 'L220-A43', 4),
    ('robot_spec', 'L4', 'L220-A47', 5),
    ('robot_spec', 'L5', 'L200-39', 6),
    ('robot_spec', 'L6', 'L200-43', 7),
    ('robot_spec', 'L7', 'L200-47', 8),
    ('robot_spec', 'L8', 'L200-48', 9);

-- Suite 사양 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('suite_spec', 'S0', '초기샘플', 1),
    ('suite_spec', 'S1', 'Suite 사양 1', 2),
    ('suite_spec', 'S2', 'Suite 사양 2', 3);

-- HW 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('hw_code', 'H1', 'New', 1),
    ('hw_code', 'H2', 'HW 버전 2', 2),
    ('hw_code', 'H3', 'HW 버전 3', 3),
    ('hw_code', 'H4', 'HW 버전 4', 4);

-- 조립 코드
INSERT INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('assembly_code', 'A0', '완제품 조립+화성시 1라인(동탄)', 1),
    ('assembly_code', 'A1', 'LMA 조립+화성시 1라인(동탄)', 2);
```

---

## 데이터베이스 다이어그램

```
┌─────────────────────────┐
│    print_history        │
├─────────────────────────┤
│ id (PK)                 │
│ serial_number (UQ)      │
│ mac_address             │
│ print_date              │
│ print_datetime          │
│ status                  │
│ error_message           │
│ prn_template            │
│ created_at              │
└─────────────────────────┘

┌─────────────────────────┐
│    lot_config           │
├─────────────────────────┤
│ id (PK) = 1             │
│ model_code              │
│ dev_code                │
│ robot_spec              │
│ suite_spec              │
│ hw_code                 │
│ assembly_code           │
│ reserved                │
│ counter                 │
│ updated_at              │
└─────────────────────────┘

┌─────────────────────────┐
│    app_config           │
├─────────────────────────┤
│ key (PK)                │
│ value                   │
│ description             │
│ updated_at              │
└─────────────────────────┘

┌─────────────────────────┐
│    code_master          │
├─────────────────────────┤
│ id (PK)                 │
│ code_type               │
│ code_value              │
│ code_name               │
│ sort_order              │
│ is_active               │
│ created_at              │
└─────────────────────────┘
```

## CRUD 쿼리 예시

### 출력 이력 저장
```sql
INSERT INTO print_history (
    serial_number, mac_address, print_date,
    print_datetime, status, prn_template
) VALUES (?, ?, ?, ?, ?, ?);
```

### LOT 정보 조회
```sql
SELECT * FROM lot_config WHERE id = 1;
```

### 생산순서 카운터 증가
```sql
UPDATE lot_config
SET counter = ?
WHERE id = 1;
```

### 출력 이력 조회 (최근 100개)
```sql
SELECT * FROM print_history
ORDER BY print_datetime DESC
LIMIT 100;
```

### 특정 날짜 출력 이력
```sql
SELECT * FROM print_history
WHERE DATE(print_datetime) = ?
ORDER BY print_datetime DESC;
```

### 시리얼 번호로 검색
```sql
SELECT * FROM print_history
WHERE serial_number LIKE ?
ORDER BY print_datetime DESC;
```

### 코드 마스터에서 드롭다운 데이터 조회
```sql
SELECT code_value, code_name
FROM code_master
WHERE code_type = ? AND is_active = 1
ORDER BY sort_order;
```

### 설정 값 조회
```sql
SELECT value FROM app_config WHERE key = ?;
```

### 설정 값 업데이트
```sql
UPDATE app_config SET value = ? WHERE key = ?;
```

## 백업 및 복구

### 백업 쿼리
```python
import shutil
from datetime import datetime

def backup_database(db_path: str, backup_dir: str):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{backup_dir}/label_printer_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path
```

### 복구 쿼리
```python
def restore_database(backup_path: str, db_path: str):
    shutil.copy2(backup_path, db_path)
```

## 데이터 무결성

### 제약 조건
1. **시리얼 번호 중복 방지**: UNIQUE 제약
2. **LOT 설정 단일 레코드**: CHECK 제약 (id = 1)
3. **출력 상태 검증**: CHECK 제약 (success/failed)
4. **자동 타임스탬프**: 트리거

### 트랜잭션 예시
```python
def print_label(db, serial_number, mac_address):
    try:
        db.begin_transaction()

        # 1. 출력 이력 저장
        db.execute(
            "INSERT INTO print_history (...) VALUES (...)"
        )

        # 2. 카운터 증가
        db.execute(
            "UPDATE lot_config SET counter = ? WHERE id = 1"
        )

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
```

## 유지보수

### 오래된 이력 삭제
```sql
-- 1년 이상 된 이력 삭제
DELETE FROM print_history
WHERE print_datetime < datetime('now', '-1 year');
```

### 데이터베이스 최적화
```sql
VACUUM;
ANALYZE;
```

### 통계 조회
```sql
-- 일일 출력 수량
SELECT DATE(print_datetime) as date, COUNT(*) as count
FROM print_history
WHERE status = 'success'
GROUP BY DATE(print_datetime)
ORDER BY date DESC
LIMIT 30;

-- LOT별 출력 수량
SELECT
    SUBSTR(serial_number, 1, 13) as lot,
    COUNT(*) as count
FROM print_history
WHERE status = 'success'
GROUP BY lot
ORDER BY count DESC;
```
