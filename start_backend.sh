cd /home/ubuntu/erp && nohup /home/ubuntu/erp/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/erp/backend.log 2>&1
