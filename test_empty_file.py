import requests

url = "http://127.0.0.1:8555/api/v1/documents/upload-initial"
# Send multipart without 'archivo'
files = {}
r = requests.post(url, files=files)
print("No file field:", r.status_code, r.text)

# Send empty file
files = {'archivo': ('', b'', 'application/octet-stream')}
r = requests.post(url, files=files)
print("Empty file:", r.status_code, r.text)
