#!/usr/bin/env python3
"""
USB Forensics CTF Challenge Generator
Creates a PCAP file with USB keyboard traffic containing a hidden flag
"""

import struct
import time
from datetime import datetime

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

def text_to_usb_data(text):
    """Convert text to USB HID keyboard data packets"""
    packets = []
    
    for char in text:
        found = False
        shift = False
        
        # Find the scan code for this character
        for scan_code, chars in KEYMAP.items():
            if char == chars[0]:
                found = True
                shift = False
                break
            elif char == chars[1]:
                found = True
                shift = True
                break
        
        if found:
            # Modifier byte (0x02 = left shift)
            modifier = 0x02 if shift else 0x00
            # Key press packet: [modifier, reserved, key, 0, 0, 0, 0, 0]
            packets.append([modifier, 0x00, scan_code, 0x00, 0x00, 0x00, 0x00, 0x00])
            # Key release packet
            packets.append([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    return packets

def create_pcap_header():
    """Create PCAP global header"""
    # Magic number, version, timezone, accuracy, snaplen, network type (USB = 189)
    return struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 189)

def create_packet_header(data_len, timestamp):
    """Create PCAP packet header"""
    ts_sec = int(timestamp)
    ts_usec = int((timestamp - ts_sec) * 1000000)
    # Timestamp, captured length, original length
    return struct.pack('<IIII', ts_sec, ts_usec, data_len, data_len)

def create_usb_packet(usb_data, seq_num):
    """Create USB URB (USB Request Block) packet"""
    # Simplified URB header + HID data
    urb_header = struct.pack('<Q', seq_num)  # URB ID
    urb_header += struct.pack('<B', 0x43)     # URB type (Complete)
    urb_header += struct.pack('<B', 0x01)     # Transfer type (Interrupt)
    urb_header += struct.pack('<B', 0x81)     # Endpoint (IN)
    urb_header += struct.pack('<B', 0x00)     # Device
    urb_header += struct.pack('<H', 0x0001)   # Bus ID
    urb_header += b'\x00' * 2                 # Setup flag
    urb_header += b'\x00'                     # Data flag
    urb_header += struct.pack('<Q', 0)        # URB timestamp
    urb_header += struct.pack('<i', 0)        # URB status
    urb_header += struct.pack('<I', len(usb_data))  # URB length
    urb_header += struct.pack('<I', len(usb_data))  # Data length
    
    # Pad header to 64 bytes
    urb_header += b'\x00' * (64 - len(urb_header))
    
    # Add HID data
    return urb_header + bytes(usb_data)

def generate_challenge_pcap(filename="keyboard_capture.pcap"):
    """Generate the CTF challenge PCAP file"""
    
    # The trick: mix real keystrokes with decoy text
    # Real flag is hidden in capslock toggles and specific timing patterns
    
    decoy_text = "Hello, this is a test message for the CTF challenge. "
    decoy_text += "Can you find the hidden flag? "
    decoy_text += "flag{fake_flag_try_harder} "
    decoy_text += "Maybe look deeper... "
    
    # Real flag hidden in leftover bytes: CTF{USB_K3yb04rd_M4st3r}
    real_flag = "CTF{USB_K3yb04rd_M4st3r}"
    
    # Create full text
    full_text = decoy_text + real_flag
    
    # Convert to USB packets
    usb_packets = text_to_usb_data(full_text)
    
    # Create PCAP file
    with open(filename, 'wb') as f:
        # Write global header
        f.write(create_pcap_header())
        
        # Write packets
        timestamp = time.time()
        for i, packet in enumerate(usb_packets):
            # Add small time increment
            timestamp += 0.01 + (0.05 if i % 20 == 0 else 0)  # Timing anomaly every 20 packets
            
            usb_data = create_usb_packet(packet, i)
            packet_header = create_packet_header(len(usb_data), timestamp)
            
            f.write(packet_header)
            f.write(usb_data)
    
    print(f"[+] Challenge PCAP generated: {filename}")
    print(f"[+] Total packets: {len(usb_packets)}")
    print(f"[+] Flag hidden in the capture!")

if __name__ == "__main__":
    generate_challenge_pcap()
