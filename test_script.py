import requests

url = "http://127.0.0.1:8555/api/v1/documents/upload-initial"
files = {'file': open('app/main.py', 'rb')}
# Wait, it returns 401 Unauthorized if no cookies!
# I need a valid session to test it! Or I can disable auth temporarily!
