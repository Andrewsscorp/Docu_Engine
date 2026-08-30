import requests

url = "http://127.0.0.1:8555/api/v1/documents/upload-initial"
files = {'file': open('app/main.py', 'rb')}
r = requests.post(url, files=files)
print(r.status_code)
print(r.text)
