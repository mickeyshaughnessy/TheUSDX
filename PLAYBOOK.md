# US Federal Data Exchange - Deployment Playbook

## Overview

Git-based deployment workflow. Commit locally, push to remote, SSH to VM, pull, restart.

---

## Initial Setup (One Time)

### 1. Digital Ocean Spaces Setup

```bash
# Create a Space in DO Console
# - Name: usdx-data
# - Region: nyc3 (or your preferred region)
# - Generate API keys (Spaces access keys)
# - Note: Access Key ID and Secret Key
```

**Space Structure:**
```
usdx-data/
├── users/              # User accounts (auto-created by app)
├── metadata/           # Dataset metadata for AI matching
└── data/               # Actual datasets
```

### 2. VM Setup

```bash
# SSH into your Digital Ocean VM
ssh root@YOUR_VM_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git

# Create deployment user (optional but recommended)
sudo useradd -m -s /bin/bash usdx
sudo usermod -aG sudo usdx
sudo su - usdx
```

### 3. Clone Repository

```bash
# On VM
cd ~
git clone YOUR_REPO_URL TheUSDX
cd TheUSDX
```

### 4. Configure Application

```bash
# On LOCAL machine, create config.py with production values
cp config.py.example config.py
nano config.py

# Fill in:
# - OPENROUTER_API_KEY
# - DO_SPACES_KEY, DO_SPACES_SECRET
# - SECRET_KEY (generate: python3 -c "import secrets; print(secrets.token_hex(32))")
# - SSL_CERT_PATH, SSL_KEY_PATH (if using SSL)

# SCP config to VM (DO NOT commit config.py!)
scp config.py YOUR_VM_IP:~/TheUSDX/config.py
```

### 5. Setup Python Environment

```bash
# On VM
cd ~/TheUSDX
pip3 install -r requirements.txt
```

### 6. SSL Certificates (Production)

```bash
# On VM
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update config.py on local machine:
SSL_CERT_PATH = '/etc/letsencrypt/live/yourdomain.com/fullchain.pem'
SSL_KEY_PATH = '/etc/letsencrypt/live/yourdomain.com/privkey.pem'

# SCP updated config
scp config.py YOUR_VM_IP:~/TheUSDX/config.py
```

### 7. Firewall

```bash
# On VM
sudo ufw allow 6732/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 8. Setup as System Service

```bash
# On VM, create systemd service
sudo nano /etc/systemd/system/usdx.service
```

Add:
```ini
[Unit]
Description=US Federal Data Exchange API Server
After=network.target

[Service]
Type=simple
User=usdx
WorkingDirectory=/home/usdx/TheUSDX
ExecStart=/usr/bin/python3 api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable usdx
sudo systemctl start usdx
sudo systemctl status usdx
```

---

## Regular Deployment Workflow

### Local Development

```bash
# Make changes
vim api_server.py

# Test locally (with local config.py)
python3 api_server.py

# Commit changes
git add api_server.py
git commit -m "Fix authentication bug"
git push origin main
```

### Deploy to VM

```bash
# SSH to VM
ssh YOUR_VM_IP

# Pull latest code
cd ~/TheUSDX
git pull

# Restart service
sudo systemctl restart usdx

# Check status
sudo systemctl status usdx

# View logs if needed
sudo journalctl -u usdx -f
```

### One-Liner Deployment

```bash
# From local machine
ssh YOUR_VM_IP "cd ~/TheUSDX && git pull && sudo systemctl restart usdx && sudo systemctl status usdx"
```

---

## Configuration Updates

When `config.py` changes:

```bash
# LOCAL machine
# Edit config.py with new values
nano config.py

# SCP to VM
scp config.py YOUR_VM_IP:~/TheUSDX/config.py

# Restart service
ssh YOUR_VM_IP "sudo systemctl restart usdx"
```

**IMPORTANT:** Never commit `config.py` to git! It's in `.gitignore`.

---

## Monitoring & Troubleshooting

### View Logs

```bash
# Real-time logs
sudo journalctl -u usdx -f

# Last 100 lines
sudo journalctl -u usdx -n 100

# Logs since last hour
sudo journalctl -u usdx --since "1 hour ago"
```

### Check Service Status

```bash
sudo systemctl status usdx
```

### Test API

```bash
# Ping endpoint
curl http://YOUR_VM_IP:6732/ping

# Or with HTTPS
curl https://yourdomain.com:6732/ping
```

### Restart Service

```bash
sudo systemctl restart usdx
```

### Stop Service

```bash
sudo systemctl stop usdx
```

---

## Data Management

### Upload Sample Data

```bash
# Install AWS CLI or use DO Spaces web interface
pip3 install awscli

# Configure for DO Spaces
aws configure
# AWS Access Key ID: YOUR_DO_SPACES_KEY
# AWS Secret Access Key: YOUR_DO_SPACES_SECRET
# Default region name: nyc3
# Default output format: json

# Upload metadata
aws s3 cp metadata/census-2023.json s3://usdx-data/metadata/census-2023.json --endpoint-url=https://nyc3.digitaloceanspaces.com

# Upload data
aws s3 cp data/census-2023.json s3://usdx-data/data/census-2023.json --endpoint-url=https://nyc3.digitaloceanspaces.com

# Or use DO console web interface
```

### Backup Users

```bash
# On VM or via AWS CLI
aws s3 sync s3://usdx-data/users/ ./backup/users/ --endpoint-url=https://nyc3.digitaloceanspaces.com
```

---

## Quick Reference

### Common Commands

```bash
# Deploy
git push && ssh VM "cd ~/TheUSDX && git pull && sudo systemctl restart usdx"

# Update config
scp config.py VM:~/TheUSDX/ && ssh VM "sudo systemctl restart usdx"

# View logs
ssh VM "sudo journalctl -u usdx -f"

# Check status
ssh VM "sudo systemctl status usdx"

# Restart
ssh VM "sudo systemctl restart usdx"
```

### File Locations

- **Code:** `/home/usdx/TheUSDX/`
- **Config:** `/home/usdx/TheUSDX/config.py`
- **Service:** `/etc/systemd/system/usdx.service`
- **SSL Certs:** `/etc/letsencrypt/live/yourdomain.com/`
- **Logs:** `sudo journalctl -u usdx`

### Important URLs

- **API:** `http://YOUR_VM_IP:6732/`
- **Ping:** `http://YOUR_VM_IP:6732/ping`
- **Docs:** `http://YOUR_VM_IP:6732/api_docs.html`
- **Spaces:** `https://cloud.digitalocean.com/spaces`
- **OpenRouter:** `https://openrouter.ai/keys`

---

## Security Checklist

- [ ] `config.py` in `.gitignore`
- [ ] Strong `SECRET_KEY` generated
- [ ] DO Spaces keys secured (not in git)
- [ ] OpenRouter API key secured (not in git)
- [ ] SSL certificates configured
- [ ] Firewall enabled (ufw)
- [ ] Service running as non-root user
- [ ] Regular system updates
- [ ] Backup strategy for user data

---

## Contact

**Mickey Shaughnessy**  
mickeyshaughnessy@gmail.com  
The Mithril Company
