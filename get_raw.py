import urllib.request
from urllib.request import urlopen
url = "https://punishments.mindbuzz.com.au/kicks.php"

header={'User-Agent': 'Mozilla/5.0'}


req = urllib.request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})


page = urlopen(req)

bytes = page.read()
raw_html = bytes.decode("utf-8")

print(raw_html)