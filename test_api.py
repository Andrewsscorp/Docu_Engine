import requests

try:
    res = requests.get("http://127.0.0.1:8000/api/v1/agn/subseries/75db37c0-c195-4dcc-8826-5013353327e9/tipologias/disponibles", 
                       headers={"Authorization": "Bearer YOUR_TOKEN_IF_NEEDED"})
    print("Status:", res.status_code)
    print("Body:", res.text)
except Exception as e:
    print("Error:", e)
