# GUADRAILS RAG WITH ENDEE - Deployment & Push Guide

## Git Push Instructions

### Prerequisites
- Git configured with your credentials
- GitHub account with push access to the repository
- You have created the repository on GitHub: https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE

### Step 1: Configure Git Authentication

```bash
# Option A: HTTPS (using personal access token)
git remote set-url origin https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git

# Option B: SSH (recommended for repeated pushes)
git remote set-url origin git@github.com:sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git
# Then generate SSH key: ssh-keygen -t ed25519 -C "your_email@example.com"
```

### Step 2: Verify Remote Configuration

```bash
# Check remote URL
git remote -v
# Should show:
# origin  https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git (fetch)
# origin  https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git (push)
```

### Step 3: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# Or if you want to use master branch
git branch -M main  # Rename to main
git push -u origin main
```

### Handling Authentication

#### For HTTPS (Password Protected)
```bash
# Use GitHub Personal Access Token (recommended)
# 1. Create token: https://github.com/settings/tokens
# 2. When prompted for password, use the token instead
git push origin main
# Type access token when prompted
```

#### For SSH (No password each time)
```bash
# Generate SSH key (if not already done)
ssh-keygen -t ed25519 -C "sowmiyan@example.com" -f ~/.ssh/sowmiyan_github

# Add to SSH agent
ssh-add ~/.ssh/sowmiyan_github

# Add public key to GitHub: https://github.com/settings/keys

# Test connection
ssh -T git@github.com
# Should output: Hi sowmiyan-s! You've successfully authenticated...

# Then push
git push -u origin main
```

## Troubleshooting Git Push

### Error: "fatal: could not read Username for 'https://github.com'"

**Solution:** Use a GitHub Personal Access Token

```bash
# Create token: https://github.com/settings/tokens
# Scopes needed: repo (all), admin:repo_hook

# When pushing, use token as password
git push origin main
# Username: sowmiyan-s
# Password: [paste your personal access token here]
```

### Error: "Permission denied (publickey)"

**Solution:** Configure SSH key

```bash
# Check SSH connection
ssh -v git@github.com

# If key issues, add it again
ssh-add -K ~/.ssh/id_ed25519  # macOS
ssh-add ~/.ssh/id_ed25519     # Linux

# Verify key is added
ssh-add -l
```

### Error: "Updates were rejected because the tip of your current branch is behind"

**Solution:** Pull before push

```bash
git pull origin main
git push origin main
```

### Error: "fatal: 'origin' does not appear to be a 'git' repository"

**Solution:** Add remote

```bash
git remote add origin https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git
git push -u origin main
```

## Deploy Locally (Development)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git
cd GUADRAILS-RAG-WITH-ENDEE

# Run setup
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start application
python app.py
```

### With Auto-Reload (Development)
```bash
python app.py --reload
```

## Docker Deployment

### Build Image
```bash
docker build -t guadrails-rag:2.0.0 .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e ENDEE_HOST=http://host.docker.internal:8080 \
  -e PORT=8000 \
  guadrails-rag:2.0.0
```

### Docker Compose
```yaml
version: "3.8"

services:
  guadrails:
    build: .
    ports:
      - "8000:8000"
    environment:
      OLLAMA_HOST: http://ollama:11434
      ENDEE_HOST: http://endee:8080
    depends_on:
      - ollama
      - endee
    networks:
      - guadrails

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - guadrails

  endee:
    image: endee:latest  # From https://github.com/endee-io/endee
    ports:
      - "8080:8080"
    volumes:
      - endee_data:/data
    networks:
      - guadrails

volumes:
  ollama_data:
  endee_data:

networks:
  guadrails:
```

## Cloud Deployment

### Render

1. **Create Render Account** - https://render.com
2. **Configure Environment Variables:**
   - `OLLAMA_HOST`: Your Ollama service URL
   - `ENDEE_HOST`: Your Endee service URL
   - `PYTHON_VERSION`: 3.11
   
3. **Deploy from GitHub:**
   ```bash
   git push origin main
   # Render auto-detects requirements.txt and deploys
   ```

### Railway

1. **Create Railway Account** - https://railway.app
2. **Connect GitHub Repository**
3. **Set Environment Variables:**
   - `OLLAMA_HOST`
   - `ENDEE_HOST`
4. **Deploy** - Railway auto-deploys on push

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Initialize
flyctl auth login
flyctl apps create <app-name>

# Deploy
flyctl deploy
```

Configure `fly.toml`:
```toml
app = "guadrails-rag"

[env]
OLLAMA_HOST = "http://ollama-service:11434"
ENDEE_HOST = "http://endee-service:8080"

[services]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

## Production Deployment with Gunicorn

### Install & Run
```bash
pip install gunicorn

# Single worker (small deployments)
gunicorn -w 1 -b 0.0.0.0:8000 guardrag.api.main:app

# Multi-worker (production)
gunicorn -w 4 -b 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker guardrag.api.main:app
```

### With Nginx Reverse Proxy
```nginx
upstream guadrails {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://guadrails;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd Service (Linux)

Create `/etc/systemd/system/guadrails.service`:

```ini
[Unit]
Description=GUADRAILS RAG WITH ENDEE
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/ubuntu/GUADRAILS-RAG-WITH-ENDEE
Environment="PATH=/home/ubuntu/venv/bin"
ExecStart=/home/ubuntu/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 guardrag.api.main:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable guadrails
sudo systemctl start guadrails
sudo systemctl status guadrails
```

## Monitoring & Logging

### View Logs
```bash
sudo journalctl -u guadrails -f  # Real-time
sudo journalctl -u guadrails -n 100  # Last 100 lines
```

### Health Check Endpoint
```bash
# Check if application is running
curl http://localhost:8000/api/health

# Check Ollama connection
curl http://localhost:8000/api/ollama/status

# Check Endee connection
curl http://localhost:8000/api/endee/status
```

## Security Checklist for Production

- [ ] Use HTTPS/TLS (Let's Encrypt via Certbot)
- [ ] Set `HOST=0.0.0.0` only for internal networks
- [ ] Use strong authentication if exposed to internet
- [ ] Keep Ollama and Endee on private network
- [ ] Regular security updates: `pip install --upgrade`
- [ ] Monitor logs for suspicious activity
- [ ] Rate limit API endpoints
- [ ] Use firewall rules

## Updating to Latest Version

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart application
systemctl restart guadrails  # If using systemd
# or
python app.py  # If running manually
```

## Rollback on Issues

```bash
# View commit history
git log --oneline

# Revert to previous version
git revert HEAD  # Creates new commit undoing changes
# or
git reset --hard HEAD~1  # Hard reset (loses changes)

# Push changes
git push origin main
```

---

For issues or questions:
- GitHub Issues: https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/issues
- Documentation: https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE#readme

