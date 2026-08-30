import requests
try:
    res = requests.get("http://127.0.0.1:8000/api/v1/agn/modal")
    print(res.status_code)
except Exception as e:
    print(e)
