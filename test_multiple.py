import requests

url = "http://127.0.0.1:8555/api/v1/documents/upload-initial"
# We need to simulate uploading multiple files with the same name "archivo"
files = [
    ('archivo', ('file1.txt', open('app/main.py', 'rb'), 'text/plain')),
    ('archivo', ('file2.txt', open('app/database.py', 'rb'), 'text/plain'))
]
r = requests.post(url, files=files)
print(r.status_code)
print(r.text)
