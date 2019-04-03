import requests
import datetime

base_url = 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_start}&date_req2={date_finish}&VAL_NM_RQ={currency_code}'
usd = 'R01235'
eur = 'R01239'
date_start = datetime.date.today().strftime('%d/%m/%Y')
date_finish = date_start


def get_kurs_usd_today():
    url = base_url.format(date_start=date_start, date_finish=date_finish, currency_code=usd)
    r = requests.get(url)
    if r.status_code == 200 and r.text:
        begin = r.text.find('<Value>')
        finish = r.text.find('</Value>')
        if begin > 0:
            return r.text[begin+7:finish]


def get_kurs_eur_today():
    url = base_url.format(date_start=date_start, date_finish=date_finish, currency_code=eur)
    r = requests.get(url)
    if r.status_code == 200 and r.text:
        begin = r.text.find('<Value>')
        finish = r.text.find('</Value>')
        if begin > 0:
            return r.text[begin+7:finish]
