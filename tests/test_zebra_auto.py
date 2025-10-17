"""
Auto test script for zebra library (0.2.1)
Tests Zebra printer control using Windows printer queues (no user input)
"""
from datetime import datetime


def test_zebra_detection():
    """Test zebra library printer detection"""

    try:
        from zebra import Zebra
        print("[1] Zebra library imported successfully")

        # Create Zebra instance
        z = Zebra()
        print("[2] Zebra instance created")

        # Get available printer queues
        print("[3] Searching for printer queues...")
        queues = z.getqueues()

        if queues:
            print(f"    Found {len(queues)} printer queue(s)")

            # Check for Zebra printers
            zebra_queues = [q for q in queues if 'zebra' in q.lower() or 'zdesigner' in q.lower() or 'zpl' in q.lower()]

            if zebra_queues:
                print(f"[4] Found {len(zebra_queues)} Zebra printer(s):")
                for i, zq in enumerate(zebra_queues, 1):
                    print(f"    [{i}] {zq}")
                return z, zebra_queues[0]
            else:
                print("[4] No Zebra printers found")
                print("    Available queues:")
                for q in queues[:5]:  # Show first 5
                    print(f"    - {q}")
                return None, None
        else:
            print("    No printer queues found")
            return None, None

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_simple_zpl(zebra_instance, queue_name):
    """Test sending simple ZPL to printer"""

    print(f"\n[5] Testing simple ZPL output to: {queue_name}")

    # Simple test label
    test_zpl = """^XA
^FO50,50^A0N,50,50^FDZebra Library Test^FS
^FO50,120^A0N,30,30^FDTime: """ + datetime.now().strftime("%H:%M:%S") + """^FS
^XZ"""

    try:
        zebra_instance.setqueue(queue_name)
        print("    Queue set successfully")
        print("    Sending test label...")

        zebra_instance.output(test_zpl)
        print("    [OK] Simple test label sent!")
        return True

    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_prn_template(zebra_instance, queue_name):
    """Test with actual PRN template"""

    print(f"\n[6] Testing PRN template output")

    prn_file = r"c:\myCodeRepoWindows\WF_LABEL_PRINTER\PSA_LABEL_ZPL_with_mac_address.prn"

    try:
        # Read template
        with open(prn_file, 'r', encoding='utf-8') as f:
            template = f.read()
        print(f"    PRN template loaded ({len(template)} bytes)")

        # Replace variables
        current_date = datetime.now().strftime("%Y.%m.%d")
        test_serial = "P10DL0S0H3A00C100001"
        test_mac = "PSAD0CF1327829495"

        zpl = template.replace("VAR_DATE", current_date)
        zpl = zpl.replace("VAR_SERIALNUMBER", test_serial)
        zpl = zpl.replace("VAR_2DBARCODE", test_serial)
        zpl = zpl.replace("VAR_MAC", test_mac)

        print(f"    Variables:")
        print(f"      Date: {current_date}")
        print(f"      Serial: {test_serial}")
        print(f"      MAC: {test_mac}")

        # Send to printer
        zebra_instance.setqueue(queue_name)
        zebra_instance.output(zpl)
        print("    [OK] PRN template label sent!")
        return True

    except FileNotFoundError:
        print(f"    [SKIP] PRN file not found: {prn_file}")
        return False
    except Exception as e:
        print(f"    [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test complete workflow with our modules"""

    print(f"\n[7] Testing full workflow integration")

    try:
        # Import our modules
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

        from zebra import Zebra
        from utils.serial_number_generator import SerialNumberGenerator
        from printer.prn_parser import PRNParser
        from database.db_manager import DatabaseManager

        print("    All modules imported")

        # Initialize
        z = Zebra()
        queues = z.getqueues()
        zebra_queues = [q for q in queues if 'zebra' in q.lower() or 'zdesigner' in q.lower()]

        if not zebra_queues:
            print("    [SKIP] No Zebra printer found")
            return False

        z.setqueue(zebra_queues[0])
        print(f"    Printer: {zebra_queues[0]}")

        # Generate serial number
        sn_gen = SerialNumberGenerator(
            model_code="P10",
            dev_code="D",
            robot_spec="L0",
            suite_spec="S0",
            hw_code="H3",
            assembly_code="A0",
            reserved="0",
            production_date="C10",
            production_sequence="0001"
        )
        serial = sn_gen.get_serial_number()
        print(f"    Serial: {serial}")

        # Parse PRN
        prn_file = r"c:\myCodeRepoWindows\WF_LABEL_PRINTER\PSA_LABEL_ZPL_with_mac_address.prn"
        parser = PRNParser(prn_file)
        parser.load_template()

        current_date = datetime.now().strftime("%Y.%m.%d")
        test_mac = "PSAD0CF1327829495"

        zpl = parser.replace_variables(current_date, serial, test_mac)
        print(f"    ZPL generated ({len(zpl)} bytes)")

        # Send to printer
        z.output(zpl)
        print("    [OK] Full workflow label sent!")

        # Save to database
        db = DatabaseManager("data/label_printer.db")
        db.save_print_history(serial, test_mac, current_date)
        print("    [OK] Saved to database")

        return True

    except Exception as e:
        print(f"    [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("Zebra Library Auto Test")
    print("="*60)

    # Step 1: Detect printer
    z, queue = test_zebra_detection()

    if z and queue:
        # Step 2: Simple test
        result1 = test_simple_zpl(z, queue)

        # Step 3: PRN template test
        result2 = test_prn_template(z, queue)

        # Step 4: Full workflow
        result3 = test_full_workflow()

        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"  Printer Detection: {'PASS' if queue else 'FAIL'}")
        print(f"  Simple ZPL Test:   {'PASS' if result1 else 'FAIL'}")
        print(f"  PRN Template Test: {'PASS' if result2 else 'FAIL'}")
        print(f"  Full Workflow:     {'PASS' if result3 else 'FAIL'}")
        print("="*60)

    else:
        print("\n[FAIL] No Zebra printer detected. Cannot proceed with tests.")

    print("\nTest Complete")
