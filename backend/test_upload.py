#!/usr/bin/env python3
"""Quick end-to-end test: login → upload → check status"""
import requests
import time
import sys

BASE = "http://localhost:8000"

# Step 1: login
print("1) Logging in...")
r = requests.post(f"{BASE}/api/v1/auth/login",
                  data={"username": "test@example.com", "password": "test123"})
if r.status_code != 200:
    print(f"   Login FAILED: {r.status_code} {r.text}")
    sys.exit(1)

token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   OK — token obtained")

# Step 2: upload
print("2) Uploading test_doc.txt...")
with open("/app/test_doc.txt", "rb") as f:
    resp = requests.post(
        f"{BASE}/api/v1/documents/upload",
        headers=headers,
        files={"file": ("test_doc.txt", f, "text/plain")},
    )
if resp.status_code not in (200, 201):
    print(f"   Upload FAILED: {resp.status_code} {resp.text}")
    sys.exit(1)

doc = resp.json()
doc_id = doc["id"]
print(f"   Uploaded OK — doc_id={doc_id}, status={doc.get('status')}")

# Step 3: poll status for up to 60 seconds
print("3) Polling status...")
for i in range(20):
    time.sleep(3)
    sr = requests.get(f"{BASE}/api/v1/documents/{doc_id}/status", headers=headers)
    if sr.status_code == 200:
        data = sr.json()
        status = data.get("status")
        print(f"   [{i+1}] status={status} word_count={data.get('word_count')} error={data.get('parse_error')}")
        if status in ("embedded", "failed"):
            break
    else:
        print(f"   [{i+1}] poll error: {sr.status_code}")

print("Done.")
