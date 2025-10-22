# CloudBreach Forensics - Solution Guide

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
