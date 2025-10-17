"""
Test 2D barcode issue - Check if serial number is correctly replaced
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.printer.prn_parser import PRNParser


def test_2d_barcode():
    """Test 2D barcode variable replacement"""

    print("="*60)
    print("2D Barcode Variable Replacement Test")
    print("="*60)

    # Load PRN template
    template_path = "templates/PSA_LABEL_ZPL_with_mac_address.prn"
    parser = PRNParser(template_path)

    # Test serial number
    test_serial = "P10DL0S0H3A00C100002"
    print(f"\nTest Serial Number: {test_serial}")
    print(f"Length: {len(test_serial)} characters")

    # Replace variables
    zpl = parser.replace_variables(
        date="2025.10.17",
        serial_number=test_serial,
        mac_address="PSAD0CF1327829495"
    )

    # Find the 2D barcode section
    print("\n" + "="*60)
    print("Checking 2D Barcode Section...")
    print("="*60)

    lines = zpl.split('\n')
    for i, line in enumerate(lines, 1):
        if 'BQ' in line or test_serial in line or 'BARCODE' in line.upper():
            print(f"Line {i:2d}: {line}")

    # Extract just the 2D barcode command
    print("\n" + "="*60)
    print("2D Barcode Command Analysis")
    print("="*60)

    for i, line in enumerate(lines):
        if '^BQ' in line:
            print(f"\nFound QR Code command at line {i+1}:")
            print(f"  {line}")
            if i+1 < len(lines):
                print(f"  {lines[i+1]}")

            # Check for ^FH command
            if '^FH' in line or (i+1 < len(lines) and '^FH' in lines[i+1]):
                print("\n  ⚠️  WARNING: ^FH (Hex mode) detected!")
                print("      This may cause character interpretation issues")

    # Check actual replacement
    print("\n" + "="*60)
    print("Variable Replacement Check")
    print("="*60)

    if "VAR_2DBARCODE" in zpl:
        print("❌ FAIL: VAR_2DBARCODE not replaced!")
    else:
        print("✅ PASS: VAR_2DBARCODE was replaced")

    if test_serial in zpl:
        print(f"✅ PASS: Serial number '{test_serial}' found in ZPL")

        # Count occurrences
        count = zpl.count(test_serial)
        print(f"   Occurrences: {count} times")

        # Find positions
        print("\n   Positions:")
        for i, line in enumerate(lines, 1):
            if test_serial in line:
                print(f"   Line {i:2d}: {line.strip()}")
    else:
        print(f"❌ FAIL: Serial number '{test_serial}' NOT found in ZPL")

    # Save to file for inspection
    output_file = "debug_zpl_output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(zpl)
    print(f"\n✅ Full ZPL saved to: {output_file}")

    # Show the problematic section
    print("\n" + "="*60)
    print("QR Code Section (Raw)")
    print("="*60)
    for i, line in enumerate(lines):
        if i >= 30 and i <= 35:  # Lines around the QR code
            print(f"{i+1:2d}: {line}")


if __name__ == "__main__":
    test_2d_barcode()
