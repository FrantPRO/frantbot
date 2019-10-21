import requests
import xml.dom.minidom

url = 'http://www.cbr.ru/scripts/XML_daily.asp'
r = requests.get(url)
if r.status_code == 200:
    dom = xml.dom.minidom.parseString(r.text)
    dom.normalize()
    date = dom.getElementsByTagName('ValCurs')[0].getAttribute('Date')
    currencies = dom.getElementsByTagName('Valute')
else:
    currencies = None


def get_rate(currency_code):
    if not currencies:
        return ''

    for parent in currencies:
        if parent.getElementsByTagName('CharCode')[0].firstChild.data == currency_code:
            rate = parent.getElementsByTagName('Value')[0].firstChild.data
            name = parent.getElementsByTagName('Name')[0].firstChild.data
            return {"currency": currency_code, "name": name,"date": date, "value": rate}
