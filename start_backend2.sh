#!/bin/bash
cd /home/ubuntu/erp
./venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 2
ps aux | grep uvicorn | grep -v grep