"""
Test script for zebra library (0.2.1)
Tests Zebra printer control using Windows printer queues
"""

def test_zebra_library():
    """Test zebra library functionality"""

    try:
        from zebra import Zebra
        print("[1] Zebra library imported successfully")
        print(f"    Location: {Zebra.__module__}")

        # Create Zebra instance
        z = Zebra()
        print("\n[2] Zebra instance created")

        # Get available printer queues
        print("\n[3] Searching for printer queues...")
        queues = z.getqueues()

        if queues:
            print(f"    Found {len(queues)} printer queue(s):")
            for i, queue in enumerate(queues, 1):
                print(f"    [{i}] {queue}")

            # Check for Zebra printers
            zebra_queues = [q for q in queues if 'zebra' in q.lower() or 'zpl' in q.lower()]

            if zebra_queues:
                print(f"\n[4] Found {len(zebra_queues)} Zebra printer(s):")
                for zq in zebra_queues:
                    print(f"    - {zq}")

                # Set the first Zebra printer as active
                selected_queue = zebra_queues[0]
                print(f"\n[5] Setting active queue to: {selected_queue}")
                z.setqueue(selected_queue)
                print("    Queue set successfully")

                # Try to get printer status (if available)
                print(f"\n[6] Checking printer capabilities...")
                print(f"    Current queue: {selected_queue}")

                # Test ZPL command
                print(f"\n[7] Testing ZPL command generation...")
                test_zpl = """^XA
^FO50,50^A0N,50,50^FDTest Label^FS
^FO50,120^A0N,30,30^FDSerial: P10DL0S0H3A00C100001^FS
^XZ"""
                print("    ZPL Command ready:")
                print("    " + test_zpl.replace("\n", "\n    "))

                # Ask user before printing
                print(f"\n[8] Ready to send test print to: {selected_queue}")
                response = input("    Send test print? (y/n): ")

                if response.lower() == 'y':
                    try:
                        z.output(test_zpl)
                        print("    ✓ Test label sent to printer!")
                    except Exception as e:
                        print(f"    ✗ Print failed: {e}")
                else:
                    print("    Test print skipped")

            else:
                print("\n[4] No Zebra printers found in queue list")
                print("    Available queues:")
                for q in queues:
                    print(f"    - {q}")

        else:
            print("    No printer queues found")
            print("    Make sure a Zebra printer is installed via Windows")

        return True

    except ImportError as e:
        print(f"✗ Failed to import zebra library: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zpl_output():
    """Test sending ZPL commands to printer"""

    print("\n" + "="*60)
    print("ZPL Output Test")
    print("="*60)

    try:
        from zebra import Zebra

        # Read our PRN template
        prn_file = r"c:\myCodeRepoWindows\WF_LABEL_PRINTER\PSA_LABEL_ZPL_with_mac_address.prn"

        print(f"\n[1] Reading PRN template: {prn_file}")
        with open(prn_file, 'r', encoding='utf-8') as f:
            template = f.read()

        print(f"    Template size: {len(template)} bytes")

        # Replace variables
        from datetime import datetime
        current_date = datetime.now().strftime("%Y.%m.%d")
        test_serial = "P10DL0S0H3A00C100001"
        test_mac = "PSAD0CF1327829495"

        zpl = template.replace("VAR_DATE", current_date)
        zpl = zpl.replace("VAR_SERIALNUMBER", test_serial)
        zpl = zpl.replace("VAR_2DBARCODE", test_serial)
        zpl = zpl.replace("VAR_MAC", test_mac)

        print(f"\n[2] Variables replaced:")
        print(f"    Date: {current_date}")
        print(f"    Serial: {test_serial}")
        print(f"    MAC: {test_mac}")

        # Get Zebra instance
        z = Zebra()
        queues = z.getqueues()
        zebra_queues = [q for q in queues if 'zebra' in q.lower() or 'zpl' in q.lower()]

        if zebra_queues:
            z.setqueue(zebra_queues[0])
            print(f"\n[3] Printer: {zebra_queues[0]}")

            response = input("\n    Send actual label to printer? (y/n): ")
            if response.lower() == 'y':
                z.output(zpl)
                print("    ✓ Label sent successfully!")
            else:
                print("    Skipped")
        else:
            print("\n[3] No Zebra printer found")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Zebra Library Test (v0.2.1)")
    print("="*60)

    success = test_zebra_library()

    if success:
        print("\n" + "="*60)
        response = input("\nRun ZPL output test with PRN template? (y/n): ")
        if response.lower() == 'y':
            test_zpl_output()

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
