import urllib.request
from xml.dom import minidom

url = "http://www.cbr.ru/scripts/XML_daily.asp"

webFile = urllib.request.urlopen(url)

if webFile.code == 200:
    data = webFile.read()
    md = minidom.parse(data)
    print(md.getElementsByTagName('USD'))
