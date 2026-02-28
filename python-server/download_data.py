import urllib.request
import re

url = 'https://raw.githubusercontent.com/Yuvix25/r3e-python-api/main/r3e_api/data/data.cs'
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = response.read().decode()

with open('data.cs', 'w') as f:
    f.write(data)
