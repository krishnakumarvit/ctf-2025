# CloudBreach Forensics CTF Challenge

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
