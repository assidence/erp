import subprocess
import time

# Start uvicorn in background
proc = subprocess.Popen(
    ["/home/ubuntu/erp/venv/bin/python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/home/ubuntu/erp",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

# Test the endpoint
import requests
try:
    r = requests.post("http://localhost:8000/api/customers/", json={"name":"Test"})
    print("Status:", r.status_code)
    print("Body:", r.text)
except Exception as e:
    print("Error:", e)
finally:
    proc.terminate()