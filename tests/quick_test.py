"""Quick hardware test"""
import sys
sys.path.insert(0, '.')

print("="*60)
print("Hardware Connection Test")
print("="*60)

# Test 1: Check imports
print("\n[1] Checking imports...")
try:
    from src.database.db_manager import DBManager
    from src.utils.serial_number_generator import SerialNumberGenerator
    from src.printer.prn_parser import PRNParser
    print("OK - All modules imported successfully")
except Exception as e:
    print(f"ERROR - {e}")
    sys.exit(1)

# Test 2: Database
print("\n[2] Testing database...")
try:
    db = DBManager(":memory:")
    db.initialize()
    lot = db.get_lot_config()
    print(f"OK - LOT: {lot['model_code']}{lot['dev_code']}, Date: {lot['production_date']}, Seq: {lot['production_sequence']}")
    db.close()
except Exception as e:
    print(f"ERROR - {e}")

# Test 3: Serial Number Generator
print("\n[3] Testing serial number generator...")
try:
    gen = SerialNumberGenerator()
    sn = gen.generate()
    print(f"OK - Generated: {sn}")
    print(f"     LOT: {gen.get_lot_code()}")
    print(f"     Date: {gen.production_date}")
    print(f"     Sequence: {gen.production_sequence}")
except Exception as e:
    print(f"ERROR - {e}")

# Test 4: PRN Parser
print("\n[4] Testing PRN parser...")
try:
    parser = PRNParser("templates/PSA_LABEL_ZPL_with_mac_address.prn")
    print(f"OK - Template loaded")
    print(f"     Has all variables: {parser.has_all_variables()}")

    zpl = parser.replace_variables("2025.10.17", "P10DL0S0H3A00C100001", "PSAD0CF1327829495")
    print(f"     ZPL generated: {len(zpl)} bytes")
except Exception as e:
    print(f"ERROR - {e}")

# Test 5: Printer Discovery
print("\n[5] Checking for Zebra printers...")
try:
    from src.printer.zebra_win_controller import ZebraWinController
    printer = ZebraWinController()
    printers = printer.get_zebra_printers()

    if printers:
        print(f"OK - Found {len(printers)} Zebra printer(s)")
        for i, p in enumerate(printers):
            print(f"     [{i+1}] {p}")
    else:
        print("WARNING - No Zebra printers found")
        print("          Printer driver installed?")
        print("          Printer powered on?")
except Exception as e:
    print(f"ERROR - {e}")

# Test 6: Serial Ports
print("\n[6] Checking serial ports...")
try:
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()

    if ports:
        print(f"OK - Found {len(ports)} serial port(s)")
        for port in ports:
            print(f"     {port.device} - {port.description}")
    else:
        print("WARNING - No serial ports found")
except Exception as e:
    print(f"ERROR - {e}")

print("\n"+"="*60)
print("Test completed!")
print("="*60)
print("\nTo run full workflow:")
print("  python src/main.py")
print("\nTo test individual modules:")
print("  python src/main.py --test serial")
print("  python src/main.py --test prn")
print("  python src/main.py --test db")
