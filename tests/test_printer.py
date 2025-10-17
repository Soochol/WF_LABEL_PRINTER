"""
Zebra 프린터 연결 테스트 스크립트
"""

import sys
sys.path.insert(0, '.')

print("="*60)
print("Zebra Printer Connection Test")
print("="*60)

# 1. Check USB backend
print("\n[1] Checking USB backend...")
try:
    import usb.core
    import usb.backend.libusb1
    import usb.backend.libusb0

    # Try to get backend
    backend = None

    # Try libusb1
    try:
        backend = usb.backend.libusb1.get_backend()
        if backend:
            print("OK - libusb1 backend found")
    except:
        pass

    # Try libusb0
    if not backend:
        try:
            backend = usb.backend.libusb0.get_backend()
            if backend:
                print("OK - libusb0 backend found")
        except:
            pass

    if not backend:
        print("ERROR - No USB backend available!")
        print("\nWindows:")
        print("  1. Download Zadig: https://zadig.akeo.ie/")
        print("  2. Install libusb-win32 or WinUSB driver for Zebra printer")
        print("\nLinux:")
        print("  sudo apt-get install libusb-1.0-0")
        sys.exit(1)

except Exception as e:
    print(f"ERROR - {e}")
    sys.exit(1)

# 2. Search for Zebra printers
print("\n[2] Searching for Zebra printers...")
ZEBRA_VID = 0x0A5F

try:
    devices = list(usb.core.find(find_all=True, idVendor=ZEBRA_VID))

    if devices:
        print(f"OK - Found {len(devices)} Zebra printer(s):")
        for i, dev in enumerate(devices):
            print(f"\n  [{i+1}] Zebra Printer")
            print(f"      VID: 0x{dev.idVendor:04X}")
            print(f"      PID: 0x{dev.idProduct:04X}")
            print(f"      Bus: {dev.bus}")
            print(f"      Address: {dev.address}")

            # Try to get manufacturer and product
            try:
                if dev.manufacturer:
                    print(f"      Manufacturer: {dev.manufacturer}")
                if dev.product:
                    print(f"      Product: {dev.product}")
                if dev.serial_number:
                    print(f"      Serial: {dev.serial_number}")
            except:
                print("      (Unable to read device strings - permission issue)")
    else:
        print("WARNING - No Zebra printers found")
        print("\nCheck:")
        print("  1. USB cable connected?")
        print("  2. Printer powered on?")
        print("  3. Driver installed correctly?")

except usb.core.NoBackendError:
    print("ERROR - No USB backend available")
    print("\nSee PRINTER_SETUP.md for installation guide")

except Exception as e:
    print(f"ERROR - {e}")

# 3. Test printer connection (if found)
if devices:
    print("\n[3] Testing printer connection...")
    try:
        from src.printer.zebra_controller import ZebraController

        printer = ZebraController()

        if printer.connect():
            print("OK - Connected to printer")

            # Check status
            status = printer.get_status()
            print(f"     Status: {status}")

            # Ask for test print
            response = input("\nDo you want to print a test label? (y/n): ")

            if response.lower() == 'y':
                print("Printing test label...")
                if printer.test_print():
                    print("OK - Test label sent to printer")
                else:
                    print("ERROR - Failed to print")

            printer.disconnect()
            print("Disconnected from printer")
        else:
            print("ERROR - Failed to connect")

    except Exception as e:
        print(f"ERROR - {e}")

print("\n" + "="*60)
print("Test completed!")
print("="*60)
print("\nNext steps:")
print("  1. If no printers found: Install USB driver (see PRINTER_SETUP.md)")
print("  2. If printer found: Run full workflow with 'python src/main.py'")
