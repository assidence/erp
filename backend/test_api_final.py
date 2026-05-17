#!/usr/bin/env python3
import subprocess
import time
import sys

# Start uvicorn in a new process
print("Starting uvicorn...")
proc = subprocess.Popen(
    ["/home/ubuntu/erp/venv/bin/python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/home/ubuntu/erp",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

# Wait for server to start
print("Waiting 5 seconds...")
time.sleep(5)

# Check if process is still running
if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print("Process died!")
    print("stdout:", stdout.decode('utf-8') if stdout else "")
    print("stderr:", stderr.decode('utf-8') if stderr else "")
    sys.exit(1)

# Test the endpoint using system python with requests
import urllib.request
import json

try:
    data = json.dumps({"name": "Test Customer"}).encode('utf-8')
    req = urllib.request.Request("http://localhost:8000/api/customers/", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", type(e).__name__, str(e))
finally:
    proc.terminate()
    proc.wait()