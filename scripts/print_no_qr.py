"""PSA_LABEL_ZPL_with_mac_address_no_qr.prn 템플릿으로 라벨 인쇄.

사용 예:
    # 단건 인쇄 (SN 직접 지정, 매수 1)
    python scripts/print_no_qr.py --sn A10ML4S0H1A00C100014

    # MAC 주소 포함 + 매수 지정
    python scripts/print_no_qr.py --sn A10ML4S0H1A00C100014 --mac AABBCCDDEEFF --copies 3

    # 파일에서 SN 목록 읽어 일괄 인쇄 (한 줄에 한 개)
    python scripts/print_no_qr.py --sn-file serials.txt

    # 네트워크 프린터로 직접 전송 (RAW/JetDirect, 포트 9100)
    python scripts/print_no_qr.py --sn A10ML4S0H1A00C100014 --host 192.168.35.79

    # 프린터 큐 직접 지정 (Windows, 미지정 시 첫 번째 Zebra 자동 선택)
    python scripts/print_no_qr.py --sn A10ML4S0H1A00C100014 --printer "ZDesigner ZT231-203dpi ZPL"

    # 실제 인쇄 없이 ZPL만 stdout으로 확인 (드라이 런)
    python scripts/print_no_qr.py --sn A10ML4S0H1A00C100014 --dry-run
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 'zebra' (Windows 전용 드라이버)가 없는 환경(Linux 개발기 등)에서도
# 드라이런이 가능하도록, 패키지 __init__.py가 트리거하는 임포트 실패를 흡수.
import importlib.util as _importlib_util
if _importlib_util.find_spec("zebra") is None:
    import types as _types
    _stub = _types.ModuleType("zebra")
    _stub.Zebra = lambda *a, **kw: None  # type: ignore[attr-defined]
    sys.modules["zebra"] = _stub

from src.printer.prn_parser import PRNParser
from src.printer.print_controller import PrintController

DEFAULT_TEMPLATE = "PSA_LABEL_ZPL_with_mac_address_no_qr.prn"
PRNS_DIR = PROJECT_ROOT / "prns"


def resolve_template(name: str) -> Path:
    p = Path(name)
    if not p.is_absolute():
        p = PRNS_DIR / name
    return p


def date_from_serial(serial_number: str) -> str:
    """SN의 생산일자 코드에서 'YYYY.MM.01' 형식 날짜 도출.

    SN 13~15번째 3글자: [연도코드][월월]
        A=2023, B=2024, C=2025, D=2026, ...
    일자는 항상 01로 고정.
    """
    code = serial_number[13:16]
    year = 2023 + (ord(code[0]) - ord("A"))
    month = int(code[1:3])
    if not (1 <= month <= 12):
        raise ValueError(f"SN의 월 부분이 유효하지 않습니다: {code}")
    return f"{year:04d}.{month:02d}.01"


def build_zpl(
    template_path: Path,
    serial_number: str,
    mac_address: str,
    copies: int,
    date_str: str | None = None,
) -> str:
    parser = PRNParser(str(template_path))
    if date_str is None:
        date_str = datetime.now().strftime("%Y.%m.%d")
    zpl = parser.replace_variables(date_str, serial_number, mac_address)
    return PrintController()._inject_print_quantity(zpl, copies)


def send_network(zpl: str, host: str, port: int = 9100, timeout: float = 5.0) -> str:
    """네트워크 프린터(RAW/JetDirect)로 ZPL을 직접 전송."""
    import socket

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(zpl.encode("utf-8"))
    return f"{host}:{port}"


def send_queue(zpl: str, printer: str | None) -> str:
    """Windows 시스템 프린터 큐로 전송."""
    from src.printer.zebra_win_controller import ZebraWinController

    ctrl = ZebraWinController()
    if printer:
        queue = printer
    else:
        zebras = ctrl.get_zebra_printers()
        if not zebras:
            raise RuntimeError(
                "Zebra 프린터를 찾을 수 없습니다. --printer 로 큐 이름을 직접 지정하세요."
            )
        queue = zebras[0]
    ctrl.connect(queue)
    ctrl.send_zpl(zpl)
    return queue


def read_serials(args: argparse.Namespace) -> list[tuple[str, str]]:
    """(serial, mac) 튜플 리스트 반환. mac은 빈 문자열 가능."""
    if args.sn:
        return [(args.sn.strip(), args.mac)]
    if args.sn_file:
        text = Path(args.sn_file).read_text(encoding="utf-8")
        return [(line.strip(), args.mac) for line in text.splitlines() if line.strip()]
    return read_csv(args.csv, args.limit, args.skip)


def read_csv(path: str, limit: int | None, skip: int = 0) -> list[tuple[str, str]]:
    """CSV(serial,code,source)에서 인쇄 대상을 읽고 빈 code는 스킵 + 중복 경고."""
    rows: list[tuple[str, str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            serial = (r.get("serial") or "").strip()
            code = (r.get("code") or "").strip()
            source = (r.get("source") or "").strip()
            if not serial:
                continue
            rows.append((serial, code, source))

    skipped = [s for s, c, _ in rows if not c]
    valid = [(s, c) for s, c, _ in rows if c]

    if skipped:
        print(f"[WARN] code 비어있는 행 {len(skipped)}건 → 건너뜀:")
        for s in skipped:
            print(f"       - {s}")

    counts = Counter(c for _, c in valid)
    dup_codes = {c for c, n in counts.items() if n > 1}
    if dup_codes:
        print(f"[WARN] 중복 MAC {len(dup_codes)}개 감지 (경고만 — 인쇄는 진행):")
        for c in sorted(dup_codes):
            sns = [s for s, cc in valid if cc == c]
            print(f"       - {c} → {', '.join(sns)}")

    if skip > 0:
        valid = valid[skip:]
        print(f"[INFO] --skip {skip} 적용 → 앞 {skip}건 건너뜀")
    if limit is not None and limit < len(valid):
        valid = valid[:limit]
        print(f"[INFO] --limit {limit} 적용 → 상위 {limit}건만 인쇄")

    return valid


def main() -> int:
    p = argparse.ArgumentParser(description="PRN 템플릿으로 라벨 인쇄")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--sn", help="시리얼 번호 1개")
    src.add_argument("--sn-file", help="SN 목록 파일 (한 줄에 1개)")
    src.add_argument("--csv", help="CSV (serial,code,source). code는 MAC")
    p.add_argument("--limit", type=int, help="--csv 사용 시 인쇄할 최대 건수")
    p.add_argument("--skip", type=int, default=0, help="--csv 사용 시 앞에서 건너뛸 건수")
    p.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        help=f"PRN 템플릿 파일명 (기본: {DEFAULT_TEMPLATE}). prns/ 하위 파일명 또는 절대경로",
    )
    p.add_argument("--mac", default="", help="MAC 주소 (대문자 영숫자). 미지정 시 빈값")
    p.add_argument("--copies", type=int, default=1, help="인쇄 매수 (기본 1)")
    date_grp = p.add_mutually_exclusive_group()
    date_grp.add_argument(
        "--date-from-sn",
        action="store_true",
        help="SN의 생산일자 코드(C09 등)로부터 YYYY.MM.01 도출. 기본은 오늘 날짜",
    )
    date_grp.add_argument(
        "--date",
        help="라벨에 인쇄할 날짜 (YYYY.MM.DD). 미지정 시 오늘",
    )
    p.add_argument("--host", help="네트워크 프린터 IP (지정 시 RAW/9100으로 전송)")
    p.add_argument("--port", type=int, default=9100, help="네트워크 프린터 포트 (기본 9100)")
    p.add_argument("--printer", help="Windows 프린터 큐 이름 (--host 미사용 시)")
    p.add_argument("--dry-run", action="store_true", help="전송 없이 ZPL만 출력")
    args = p.parse_args()

    template_path = resolve_template(args.template)
    if not template_path.exists():
        print(f"ERROR: 템플릿이 없습니다: {template_path}", file=sys.stderr)
        return 2

    items = read_serials(args)
    target = (
        f"network {args.host}:{args.port}" if args.host
        else f"queue {args.printer or '(자동)'}"
    )
    print(f"[INFO] 템플릿: {template_path.name}")
    print(f"[INFO] 대상: {target}")
    print(f"[INFO] 인쇄 대상 {len(items)}건, 매수 {args.copies}")

    destination: str | None = None
    for i, (sn, mac) in enumerate(items, 1):
        if args.date_from_sn:
            date_str = date_from_serial(sn)
        elif args.date:
            date_str = args.date
        else:
            date_str = None
        zpl = build_zpl(template_path, sn, mac, args.copies, date_str)
        if args.dry_run:
            print(f"\n----- [{i}/{len(items)}] {sn} (MAC={mac or '(빈값)'}, DATE={date_str or '오늘'}) -----")
            print(zpl)
            continue
        if args.host:
            destination = send_network(zpl, args.host, args.port)
        else:
            destination = send_queue(zpl, args.printer)
        print(f"[OK] ({i}/{len(items)}) {sn} MAC={mac} → {destination}")

    if args.dry_run:
        print("\n[DRY-RUN] 실제 인쇄는 수행하지 않았습니다.")
    else:
        print(f"\n[DONE] {len(items)}건 전송 완료 → {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
