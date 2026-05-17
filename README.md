# ERP System Deployment Guide

## System Requirements

- **OS**: Ubuntu 20.04 LTS or later
- **Node.js**: v18.x or later
- **Python**: 3.10 or later
- **Nginx**: 1.18+
- **WSL**: Required for Windows development environment

## Installation Steps

1. **Install Python virtual environment and dependencies**:
   cd /home/ubuntu/erp/backend
   python3 -m venv /home/ubuntu/erp/venv
   /home/ubuntu/erp/venv/bin/pip install -r requirements.txt

2. **Install Node.js dependencies**:
   cd /home/ubuntu/erp/frontend
   npm install

3. **Copy systemd service files**:
   sudo cp /home/ubuntu/erp/erp-backend.service /etc/systemd/system/
   sudo cp /home/ubuntu/erp/erp-frontend.service /etc/systemd/system/

4. **Configure Nginx**:
   sudo cp /home/ubuntu/erp/nginx.conf /etc/nginx/sites-available/erp
   sudo ln -s /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/

5. **Reload systemd and nginx**:
   sudo systemctl daemon-reload
   sudo systemctl enable erp-backend erp-frontend

## Starting Services

### Build Frontend (First time or updates):
bash /home/ubuntu/erp/build.sh

### Start Backend Service:
sudo systemctl start erp-backend

### Start Frontend Service:
sudo systemctl start erp-frontend

### View Service Status:
sudo systemctl status erp-backend
sudo systemctl status erp-frontend

## Access Addresses

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost | 80 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |

## Logs

View service logs:
sudo journalctl -u erp-backend -f
sudo journalctl -u erp-frontend -f

## Troubleshooting

1. **Backend fails to start**: Check Python virtual environment path and dependencies
2. **Frontend not accessible**: Verify nginx is running and dist/ folder exists
3. **Port conflicts**: Ensure ports 80 and 8000 are not in use
