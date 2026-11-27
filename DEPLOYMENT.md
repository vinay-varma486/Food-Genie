# FoodGenie Production Deployment Guide

This document outlines instructions for deploying the **FoodGenie** application in production environments.

---

## 1. System Architecture Overview

```
                        [ Client Web Browser / Mobile ]
                                      │
                                      ▼ HTTPS (Port 443)
                        [ Nginx Reverse Proxy / Load Balancer ]
                                      │
                  ┌───────────────────┴───────────────────┐
                  ▼                                       ▼
       [ Frontend (Static SPA) ]               [ FastAPI Backend API ]
       Vite + React + Tailwind CSS             Python 3.11+ / Uvicorn Workers
       (Served via Nginx / CDN)                (Port 8000 via Systemd / Docker)
                                                          │
                                         ┌────────────────┴────────────────┐
                                         ▼                                 ▼
                             [ PostgreSQL Database ]             [ External LLM APIs ]
                             Food, User & Clinical Data          Google Gemini / OpenAI
```

---

## 2. Production Security & Environment Checklist

Before deploying, ensure:
1. **`SECRET_KEY`**: Replace default secret key with a cryptographically secure 32-byte hex string:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. **`DATABASE_URL`**: Point to a secured, authenticated PostgreSQL instance.
3. **CORS Origins**: Limit `BACKEND_CORS_ORIGINS` to exact production domain(s) (e.g. `["https://app.foodgenie.ai"]`).
4. **HTTPS / SSL**: Mandatory for speech recognition. Modern browsers (Chrome, Edge, Safari, Firefox) restrict `navigator.mediaDevices` and the `Web Speech API` to HTTPS or `localhost`.
5. **API Keys**: Store `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `GNANI_API_KEY` securely in `.env` without checking them into version control.

---

## 3. Docker Deployment (Recommended)

### A. Backend `Dockerfile`
Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### B. Frontend `Dockerfile`
Create `frontend/Dockerfile`:
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### C. `docker-compose.yml`
Create `docker-compose.yml` in the project root:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: foodgenie_db
      POSTGRES_USER: foodgenie_user
      POSTGRES_PASSWORD: strong_postgres_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U foodgenie_user -d foodgenie_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
    restart: always
    depends_on:
      db:
        condition: service_healthy
    environment:
      PROJECT_NAME: "FOODGENIE"
      API_V1_STR: "/api/v1"
      SECRET_KEY: "change_me_to_a_secure_random_key_in_production"
      DATABASE_URL: "postgresql://foodgenie_user:strong_postgres_password_here@db:5432/foodgenie_db"
      LLM_PROVIDER: "gemini"
      GEMINI_API_KEY: "${GEMINI_API_KEY}"
      DEFAULT_LANGUAGE: "en"
      SUPPORTED_LANGUAGES: '["en", "te", "hi", "ta", "kn"]'
      BACKEND_CORS_ORIGINS: '["https://app.foodgenie.ai", "http://localhost:5173"]'
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Run with:
```bash
docker compose up -d --build
```

---

## 4. Bare-Metal / VPS Deployment (Ubuntu / Debian)

### A. Backend Setup via Systemd
1. Clone repository to `/var/www/foodgenie`:
   ```bash
   git clone <repo_url> /var/www/foodgenie
   cd /var/www/foodgenie/backend
   ```
2. Create and activate Python virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install gunicorn
   ```
3. Create Systemd Service File `/etc/systemd/system/foodgenie-backend.service`:
   ```ini
   [Unit]
   Description=FoodGenie FastAPI Application
   After=network.target postgresql.service

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/foodgenie/backend
   EnvironmentFile=/var/www/foodgenie/backend/.env
   ExecStart=/var/www/foodgenie/backend/venv/bin/gunicorn main:app \
       -w 4 \
       -k uvicorn.workers.UvicornWorker \
       -b 127.0.0.1:8000 \
       --access-logfile /var/log/foodgenie_access.log \
       --error-logfile /var/log/foodgenie_error.log

   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
4. Enable and start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable foodgenie-backend
   sudo systemctl start foodgenie-backend
   sudo systemctl status foodgenie-backend
   ```

### B. Frontend Static Build
1. Navigate to `frontend/`:
   ```bash
   cd /var/www/foodgenie/frontend
   npm ci
   npm run build
   ```
2. Built assets will reside in `/var/www/foodgenie/frontend/dist`.

### C. Nginx Reverse Proxy Configuration
Create `/etc/nginx/sites-available/foodgenie`:
```nginx
server {
    listen 80;
    server_name app.foodgenie.ai api.foodgenie.ai;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.foodgenie.ai;

    ssl_certificate /etc/letsencrypt/live/app.foodgenie.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.foodgenie.ai/privkey.pem;

    root /var/www/foodgenie/frontend/dist;
    index index.html;

    # SPA Client Routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Swagger Documentation
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/foodgenie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### D. SSL / TLS via Let's Encrypt Certbot
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d app.foodgenie.ai
```

---

## 5. Voice Services & HTTPS Requirements

- **Microphone Permissions**: Web standards require HTTPS for `navigator.mediaDevices.getUserMedia` and the `webkitSpeechRecognition` API. On `http://localhost`, browsers waive this restriction for local development, but in production, an SSL certificate (Let's Encrypt) is mandatory.
- **Language Code Fallback**: If a client device lacks a native Telugu (`te-IN`) or Hindi (`hi-IN`) speech engine, the frontend Voice Provider automatically renders recognized responses as formatted text with visual captions, preventing any audio playback interruption.

---

## 6. Health Checks & Verification

- **API Health Endpoint**: `GET https://app.foodgenie.ai/health` -> `{"status": "healthy", "service": "foodgenie-fastapi"}`
- **Interactive Swagger Docs**: `GET https://app.foodgenie.ai/docs`
- **Automated Verification**:
  ```bash
  cd /var/www/foodgenie/backend
  source venv/bin/activate
  python -m pytest tests/ -v
  ```
  Expected: **40 passed (100%)**.

