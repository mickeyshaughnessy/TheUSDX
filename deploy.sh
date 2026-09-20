#!/bin/bash
# Deployment script for TheUSDX (Acme Redactors)
# Usage: ./deploy.sh

set -e

SERVER="root@143.110.131.237"
SSH_KEY="~/.ssh/id_ed25519"
DEPLOY_PATH="/var/www/TheUSDX"
SERVICE_NAME="usdx.service"

echo "Deploying TheUSDX to $SERVER..."

# 1. Sync config
if [ -f "config.py" ]; then
    echo "Syncing config.py..."
    scp -i "$SSH_KEY" config.py "$SERVER:$DEPLOY_PATH/config.py"
fi

# 2. Pull latest code on server
echo "Pulling latest code..."
ssh -i "$SSH_KEY" "$SERVER" << 'ENDSSH'
set -e
cd /var/www/TheUSDX
git stash 2>/dev/null || true
git pull origin main
git stash pop 2>/dev/null || true
echo "Code updated: $(git rev-parse --short HEAD)"
ENDSSH

# 3. Install systemd unit (gunicorn timeout) and lengthen nginx proxy timeout
echo "Updating service unit and nginx timeouts..."
ssh -i "$SSH_KEY" "$SERVER" << 'ENDSSH'
set -e
cp /var/www/TheUSDX/usdx.service /etc/systemd/system/usdx.service
systemctl daemon-reload
python3 - << 'PY'
from pathlib import Path
p = Path('/etc/nginx/sites-enabled/themithrilcompany.com')
text = p.read_text()
old = """    location / {
        proxy_pass http://localhost:6732;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }"""
new = """    location / {
        proxy_pass http://localhost:6732;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s;
        proxy_send_timeout 180s;
    }"""
if old in text:
    p.write_text(text.replace(old, new, 1))
    print('nginx location / timeout set to 180s')
elif 'proxy_read_timeout 180s' in text:
    print('nginx already has 180s timeout')
else:
    print('WARN: did not find expected location / block')
PY
nginx -t
systemctl reload nginx
ENDSSH

# 4. Restart service
echo "Restarting $SERVICE_NAME..."
ssh -i "$SSH_KEY" "$SERVER" "systemctl restart $SERVICE_NAME && sleep 2 && systemctl is-active $SERVICE_NAME"

echo "Deployment complete."
