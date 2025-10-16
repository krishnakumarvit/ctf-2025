#!/usr/bin/env python3
"""
USB Forensics CTF Challenge - Solution Script
Extracts keystrokes from USB keyboard packet capture
"""

import struct
import sys

# USB HID Keyboard scan codes (US layout)
KEYMAP = {
    0x04: ['a', 'A'], 0x05: ['b', 'B'], 0x06: ['c', 'C'], 0x07: ['d', 'D'],
    0x08: ['e', 'E'], 0x09: ['f', 'F'], 0x0A: ['g', 'G'], 0x0B: ['h', 'H'],
    0x0C: ['i', 'I'], 0x0D: ['j', 'J'], 0x0E: ['k', 'K'], 0x0F: ['l', 'L'],
    0x10: ['m', 'M'], 0x11: ['n', 'N'], 0x12: ['o', 'O'], 0x13: ['p', 'P'],
    0x14: ['q', 'Q'], 0x15: ['r', 'R'], 0x16: ['s', 'S'], 0x17: ['t', 'T'],
    0x18: ['u', 'U'], 0x19: ['v', 'V'], 0x1A: ['w', 'W'], 0x1B: ['x', 'X'],
    0x1C: ['y', 'Y'], 0x1D: ['z', 'Z'], 0x1E: ['1', '!'], 0x1F: ['2', '@'],
    0x20: ['3', '#'], 0x21: ['4', '$'], 0x22: ['5', '%'], 0x23: ['6', '^'],
    0x24: ['7', '&'], 0x25: ['8', '*'], 0x26: ['9', '('], 0x27: ['0', ')'],
    0x28: ['\n', '\n'], 0x2C: [' ', ' '], 0x2D: ['-', '_'], 0x2E: ['=', '+'],
    0x2F: ['[', '{'], 0x30: [']', '}'], 0x33: [';', ':'], 0x34: ["'", '"'],
    0x36: [',', '<'], 0x37: ['.', '>'], 0x38: ['/', '?'], 0x39: ['CAPS', 'CAPS']
}

def parse_pcap(filename):
    """Parse PCAP file and extract USB HID data"""
    with open(filename, 'rb') as f:
        # Read global header
        global_header = f.read(24)
        magic = struct.unpack('<I', global_header[0:4])[0]
        
        if magic != 0xa1b2c3d4:
            print("[-] Invalid PCAP file")
            return []
        
        packets = []
        
        # Read packets
        while True:
            # Read packet header
            packet_header = f.read(16)
            if len(packet_header) < 16:
                break
            
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('<IIII', packet_header)
            
            # Read packet data
            packet_data = f.read(incl_len)
            if len(packet_data) < incl_len:
                break
            
            # Skip URB header (64 bytes) and extract HID data
            if len(packet_data) >= 64 + 8:
                hid_data = packet_data[64:64+8]
                packets.append({
                    'timestamp': ts_sec + ts_usec / 1000000.0,
                    'data': hid_data
                })
        
        return packets

def extract_keystrokes(packets):
    """Extract keystrokes from USB HID data"""
    keystrokes = []
    
    for packet in packets:
        data = packet['data']
        
        # USB HID format: [modifier, reserved, key1, key2, key3, key4, key5, key6]
        modifier = data[0]
        key = data[2]
        
        # Skip empty packets (key release)
        if key == 0x00:
            continue
        
        # Check if shift is pressed
        shift = (modifier & 0x02) != 0
        
        # Lookup key in keymap
        if key in KEYMAP:
            char = KEYMAP[key][1 if shift else 0]
            keystrokes.append(char)
    
    return ''.join(keystrokes)

def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <pcap_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    print(f"[*] Parsing PCAP file: {filename}")
    packets = parse_pcap(filename)
    print(f"[+] Found {len(packets)} USB packets")
    
    print("\n[*] Extracting keystrokes...")
    text = extract_keystrokes(packets)
    
    print("\n[+] Recovered text:")
    print("=" * 80)
    print(text)
    print("=" * 80)
    
    # Search for flags
    if 'CTF{' in text or 'flag{' in text.lower():
        print("\n[+] Flag patterns found in text!")
        import re
        flags = re.findall(r'[Cc][Tt][Ff]\{[^}]+\}|[Ff][Ll][Aa][Gg]\{[^}]+\}', text)
        for flag in flags:
            print(f"    {flag}")

if __name__ == "__main__":
    main()
