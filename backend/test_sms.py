import requests
import json

base_url = "http://localhost:5000/api"

# 1. Register/Login
try:
    requests.post(f"{base_url}/auth/register", json={"username": "testuser_sms1", "email": "sms1@test.com", "password": "pass"})
except:
    pass

res = requests.post(f"{base_url}/auth/login", json={"username": "testuser_sms1", "password": "pass"})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("--- Testing Upload ---")
upload_res = requests.post(f"{base_url}/upload-sms", json={
    "messages": [
        {"sender": "123456", "body": "Test message body", "date": "2026-04-10T12:00:00Z"}
    ]
}, headers=headers)
print(upload_res.status_code, upload_res.text)

print("--- Testing Fetch Messages ---")
get_res = requests.get(f"{base_url}/messages", headers=headers)
print(get_res.status_code, get_res.text)

print("--- Testing Stats Page (Dashboard Error) ---")
stats_res = requests.get(f"http://localhost:5000/api/dashboard/stats", headers=headers)
print(stats_res.status_code, stats_res.text)

print("--- Testing History Page (Dashboard Error) ---")
history_res = requests.get(f"http://localhost:5000/api/dashboard/history", headers=headers)
print(history_res.status_code, history_res.text)
