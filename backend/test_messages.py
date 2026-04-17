import requests

base_url = "http://localhost:5000/api"
res = requests.post(f"{base_url}/auth/login", json={"username": "testuser_sms1", "password": "pass"})
token = res.json().get("access_token")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{base_url}/messages", headers=headers)
    print("Messages Status:", r.status_code)
    print("Messages Preview:", r.text[:500])
else:
    print("Login failed", res.text)
