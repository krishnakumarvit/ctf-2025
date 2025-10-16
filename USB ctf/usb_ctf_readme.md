# USB Forensics CTF Challenge: "Lost Keystrokes"

## Challenge Description

**Category:** Forensics  
**Difficulty:** Medium  
**Points:** 350

**Story:**
```
We intercepted a USB packet capture from a suspected insider threat's 
workstation. Our initial analysis shows keyboard activity, but the user 
claims they were just typing a test message. However, our intel suggests 
they were exfiltrating sensitive data. 

Can you recover what was actually typed and find the secret access code?

Flag format: CTF{...}
```

**Files Provided:**
- `keyboard_capture.pcap` - USB packet capture file

---

## Deployment Instructions

### Setup

1. **Generate the Challenge File:**
```bash
python3 generate_challenge.py
```

This creates `keyboard_capture.pcap` with the hidden flag.

2. **Verify the Challenge:**
```bash
# Check file size and packet count
ls -lh keyboard_capture.pcap
tshark -r keyboard_capture.pcap -c 10
```

3. **Test the Solution:**
```bash
python3 solution.py keyboard_capture.pcap
```

### File Structure
```
usb-forensics-ctf/
├── README.md                    (this file)
├── challenge/
│   ├── keyboard_capture.pcap   (generated challenge file)
│   └── description.txt          (challenge description)
├── solution/
│   ├── solution.py              (solution script)
│   ├── walkthrough.md           (detailed walkthrough)
│   └── flag.txt                 (the flag)
└── generate_challenge.py        (challenge generator)
```

---

## Solution Walkthrough

### Step 1: Initial Analysis

Open the PCAP in Wireshark:
```bash
wireshark keyboard_capture.pcap
```

Observations:
- USB packets with URB_INTERRUPT transfers
- Endpoint 0x81 (IN direction)
- Regular 8-byte data payloads

### Step 2: Understanding USB HID Protocol

USB keyboards use the HID (Human Interface Device) protocol. Each keystroke generates:
- **8 bytes of data:** `[Modifier, Reserved, Key1, Key2, Key3, Key4, Key5, Key6]`
  - Byte 0: Modifier keys (Shift, Ctrl, Alt, etc.)
  - Byte 1: Reserved (always 0x00)
  - Bytes 2-7: Up to 6 simultaneous key presses

**Key points:**
- Modifier byte: `0x02` = Left Shift, `0x01` = Left Ctrl
- Scan codes map to physical keys (not characters)
- Key press followed by key release (all zeros)

### Step 3: Extract USB Data

Using tshark:
```bash
tshark -r keyboard_capture.pcap -T fields -e usb.capdata > usb_data.txt
```

Or use the provided Python solution script.

### Step 4: Parse HID Data

Map scan codes to characters using the USB HID keymap:
- 0x04 = 'a', 0x05 = 'b', ..., 0x1D = 'z'
- With shift modifier: uppercase letters
- 0x2C = space, 0x28 = enter

### Step 5: Run Solution Script

```bash
python3 solution.py keyboard_capture.pcap
```

The script will:
1. Parse the PCAP file
2. Extract USB HID data packets
3. Convert scan codes to characters
4. Display the recovered text

### Step 6: Find the Flag

The recovered text contains:
```
Hello, this is a test message for the CTF challenge. Can you find the 
hidden flag? flag{fake_flag_try_harder} Maybe look deeper... 
CTF{USB_K3yb04rd_M4st3r}
```

**Flag:** `CTF{USB_K3yb04rd_M4st3r}`

---

## Technical Details

### USB HID Keyboard Protocol

**Packet Structure:**
```
Byte 0: Modifier byte
  Bit 0: Left Ctrl
  Bit 1: Left Shift
  Bit 2: Left Alt
  Bit 3: Left GUI (Windows/Command key)
  Bit 4: Right Ctrl
  Bit 5: Right Shift
  Bit 6: Right Alt
  Bit 7: Right GUI

Byte 1: Reserved (0x00)

Bytes 2-7: Pressed keys (scan codes)
```

**Common Scan Codes:**
- Letters: 0x04-0x1D (a-z)
- Numbers: 0x1E-0x27 (1-0)
- Special keys: 0x28 (Enter), 0x2C (Space), 0x2A (Backspace)

### Challenge Tricks

1. **Decoy flag:** Contains `flag{fake_flag_try_harder}` to mislead players
2. **Mixed content:** Real flag appears after innocuous text
3. **Timing variations:** Small timing anomalies (red herring)

### Learning Objectives

- Understanding USB packet capture analysis
- USB HID protocol internals
- Binary data parsing
- Forensic artifact recovery
- Pattern recognition in network traffic

---

## Alternative Tools

### Using Wireshark
1. Open PCAP: `wireshark keyboard_capture.pcap`
2. Filter: `usb.capdata`
3. Manually map bytes 2-7 using HID keymap

### Using tshark + Python
```bash
tshark -r keyboard_capture.pcap -T fields -e usb.capdata | \
python3 -c "import sys; [print(line.strip()) for line in sys.stdin if line.strip()]"
```

### Using Cyberchef
1. Extract hex data from PCAP
2. Use "From Hex" recipe
3. Parse bytes manually

---

## Hints for Players

**Hint 1 (25 points):** USB keyboards use the HID protocol. Each keystroke is an 8-byte packet.

**Hint 2 (50 points):** Look at byte offset 2 in each USB data packet - that's the scan code for the pressed key.

**Hint 3 (75 points):** Check byte offset 0 for the modifier byte. 0x02 means shift is pressed.

---

## Scoring

- **Quick solve (<30 min):** Full points (350)
- **With 1 hint:** 325 points
- **With 2 hints:** 300 points
- **With 3 hints:** 275 points

---

## Additional Challenges (Hard Mode)

For experienced players, create advanced variants:

1. **Mixed Languages:** Use international keyboard layouts
2. **Encrypted Text:** Keystroke data is base64 encoded
3. **Multi-Device:** Mix keyboard with mouse movements
4. **Corrupted Packets:** Intentionally corrupt some packets
5. **Steganography:** Hide flag in packet timing intervals

---

## Credits

**Challenge Author:** [Your CTF Team]  
**Difficulty Rating:** Medium (3/5)  
**Estimated Solve Time:** 20-45 minutes  
**Tools Required:** Wireshark, Python, or tshark

---

## Support

For questions or issues:
- Check the hints system
- Review USB HID specification
- Google "USB keyboard forensics"
- Ask organizers in #ctf-help channel

**Good luck and happy hacking! 🚩**
