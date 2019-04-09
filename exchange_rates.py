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

usd = 'R01235'
eur = 'R01239'


def get_rate_usd():
    if not currencies:
        return ''

    for parent in currencies:
        if parent.getAttribute('ID') == usd:
            rate = parent.getElementsByTagName('Value')[0].firstChild.data
            return {'currency': 'USD', 'date': date, 'value': rate}


def get_rate_eur():
    if not currencies:
        return ''

    for parent in currencies:
        if parent.getAttribute('ID') == eur:
            rate = parent.getElementsByTagName('Value')[0].firstChild.data
            return {'currency': 'EUR', 'date': date, 'value': rate}
