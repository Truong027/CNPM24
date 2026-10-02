import requests
import json

url = "http://127.0.0.1:5000/get_plates"
print(f"Calling {url}...")
try:
    r = requests.get(url, timeout=10)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"Error: {e}")
