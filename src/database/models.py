"""
데이터베이스 스키마 정의
"""

# 테이블 생성 SQL
CREATE_TABLES = """
-- 출력 이력
CREATE TABLE IF NOT EXISTS print_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL,
    mac_address TEXT NOT NULL,
    print_date DATE NOT NULL,
    print_datetime DATETIME NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
    error_message TEXT,
    prn_template TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(serial_number)
);

-- LOT 설정
CREATE TABLE IF NOT EXISTS lot_config (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    model_code TEXT NOT NULL,
    dev_code TEXT NOT NULL,
    robot_spec TEXT NOT NULL,
    suite_spec TEXT NOT NULL,
    hw_code TEXT NOT NULL,
    assembly_code TEXT NOT NULL,
    reserved TEXT NOT NULL DEFAULT '0',
    production_date TEXT NOT NULL,       -- 생산일자 코드 (C10 = 2025년 10월)
    production_sequence TEXT NOT NULL,   -- 생산순서 (0001)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 애플리케이션 설정
CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 코드 마스터
CREATE TABLE IF NOT EXISTS code_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_type TEXT NOT NULL,
    code_value TEXT NOT NULL,
    code_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code_type, code_value)
);
"""

# 인덱스 생성 SQL
CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_print_history_date
    ON print_history(print_datetime DESC);

CREATE INDEX IF NOT EXISTS idx_print_history_serial
    ON print_history(serial_number);

CREATE INDEX IF NOT EXISTS idx_print_history_mac
    ON print_history(mac_address);

CREATE INDEX IF NOT EXISTS idx_print_history_status
    ON print_history(status);

CREATE INDEX IF NOT EXISTS idx_code_master_type
    ON code_master(code_type, sort_order);
"""

# 트리거 생성 SQL
CREATE_TRIGGERS = """
-- LOT 설정 업데이트 시 타임스탬프 자동 갱신
CREATE TRIGGER IF NOT EXISTS update_lot_config_timestamp
AFTER UPDATE ON lot_config
BEGIN
    UPDATE lot_config SET updated_at = CURRENT_TIMESTAMP WHERE id = 1;
END;

-- 앱 설정 업데이트 시 타임스탬프 자동 갱신
CREATE TRIGGER IF NOT EXISTS update_app_config_timestamp
AFTER UPDATE ON app_config
BEGIN
    UPDATE app_config SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
END;
"""

# 초기 데이터 삽입 SQL
INSERT_INITIAL_DATA = """
-- LOT 설정 초기 데이터
INSERT OR IGNORE INTO lot_config (
    id, model_code, dev_code, robot_spec, suite_spec,
    hw_code, assembly_code, reserved, production_date, production_sequence
) VALUES (
    1, 'P10', 'D', 'L0', 'S0', 'H3', 'A0', '0', 'C10', '0001'
);

-- 앱 설정 초기 데이터
INSERT OR IGNORE INTO app_config (key, value, description) VALUES
    ('printer_selection', '자동 검색 (권장)', '프린터 선택'),
    ('prn_template', 'PSA_LABEL_ZPL_with_mac_address.prn', '기본 PRN 템플릿'),
    ('serial_port', 'COM3', 'MCU 시리얼 포트'),
    ('serial_baudrate', '115200', 'MCU 보드레이트'),
    ('serial_timeout', '30', 'MAC 수신 타임아웃 (초)'),
    ('auto_increment', 'true', '생산순서 자동 증가 활성화'),
    ('use_mac_in_label', 'false', 'MAC 주소 라벨 사용 여부'),
    ('backup_enabled', 'true', 'DB 백업 활성화'),
    ('backup_interval', '3600', '백업 주기 (초)'),
    ('last_backup', '', '마지막 백업 시각');

-- 코드 마스터 초기 데이터
-- 모델명 코드
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('model_code', 'P10', 'PSP 1.0', 1),
    ('model_code', 'W10', 'WSP 1.0', 2),
    ('model_code', 'M10', 'M10', 3),
    ('model_code', 'A10', 'PSA 1.0', 4);

-- 개발 코드
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('dev_code', 'P', 'Pilot', 1),
    ('dev_code', 'M', 'Manufacturing(양산)', 2),
    ('dev_code', 'T', 'Test', 3),
    ('dev_code', 'D', 'Demo(시연)', 4),
    ('dev_code', 'R', 'Replacement(교체품)', 5);

-- 로봇 사양 코드
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
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
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('suite_spec', 'S0', '초기샘플', 1),
    ('suite_spec', 'S1', 'Suite 사양 1', 2),
    ('suite_spec', 'S2', 'Suite 사양 2', 3);

-- HW 코드
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('hw_code', 'H1', 'New', 1),
    ('hw_code', 'H2', 'HW 버전 2', 2),
    ('hw_code', 'H3', 'HW 버전 3', 3),
    ('hw_code', 'H4', 'HW 버전 4', 4);

-- 조립 코드
INSERT OR IGNORE INTO code_master (code_type, code_value, code_name, sort_order) VALUES
    ('assembly_code', 'A0', '완제품 조립+화성시 1라인(동탄)', 1),
    ('assembly_code', 'A1', 'LMA 조립+화성시 1라인(동탄)', 2);
"""
