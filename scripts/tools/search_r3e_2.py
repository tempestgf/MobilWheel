import urllib.request
import urllib.parse
import re

url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote('RaceRoom shared memory python')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as response:
    html = response.read().decode()
    for match in re.findall(r'<a class="result__url" href="([^"]+)"', html)[:5]:
        print(match)
