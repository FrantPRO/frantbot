import requests
import xml.dom.minidom
import html.parser
import urllib.request
import urllib.parse
import re
from langdetect import detect

url = "http://www.cbr.ru/scripts/XML_daily.asp"
r = requests.get(url)
if r.status_code == 200:
    dom = xml.dom.minidom.parseString(r.text)
    dom.normalize()
    date = dom.getElementsByTagName("ValCurs")[0].getAttribute("Date")
    currencies = dom.getElementsByTagName("Valute")
else:
    currencies = None


def get_currency_rate(currency_code):
    if not currencies:
        return ""

    for parent in currencies:
        if parent.getElementsByTagName("CharCode")[0].firstChild.data == currency_code:
            rate = parent.getElementsByTagName("Value")[0].firstChild.data
            name = parent.getElementsByTagName("Name")[0].firstChild.data
            return {"currency": currency_code, "name": name, "date": date, "value": rate}


def transliterate_text(text):
    result = ""
    dic = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
           "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
           "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h",
           "ц": "ts", "ч": "ch", "ш": "sh", "щ": "scz", "ъ": "", "ы": "y", "ь": "", "э": "e",
           "ю": "u", "я": "ja", "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "E",
           "Ж": "zh", "З": "z", "И": "i", "Й": "i", "К": "k", "Л": "l", "М": "m", "Н": "n",
           "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "H",
           "Ц": "Ts", "Ч": "Ch", "Ш": "Sh", "Щ": "Scz", "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E",
           "Ю": "U", "Я": "Ya"}
    for i in range(len(text)):
        if text[i] in dic:
            sim = dic[text[i]]
        else:
            sim = text[i]
        result += sim
    return result


def translate(text_for_translate: str) -> str:
    base_link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s"
    from_language = detect(text_for_translate)
    if from_language == "ru":
        to_language = "en"
    else:
        to_language = "ru"
    text_for_translate = urllib.parse.quote(text_for_translate)
    link = base_link % (to_language, from_language, text_for_translate)
    agent = {'User-Agent':
                 "Mozilla/4.0 (\
                 compatible;\
                 MSIE 6.0;\
                 Windows NT 5.1;\
                 SV1;\
                 .NET CLR 1.1.4322;\
                 .NET CLR 2.0.50727;\
                 .NET CLR 3.0.04506.30\
                 )"}
    request = urllib.request.Request(link, headers=agent)
    raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="t0">(.*?)<'
    re_result = re.findall(expr, data)
    if len(re_result) == 0:
        result = ""
    else:
        result = html.unescape(re_result[0])
    return result


def detect_lang(text):
    return detect(text)


def weather_forecast(city, key):
    resp = requests.get("https://api.openweathermap.org/data/2.5/find",
                        params={'q': city, 'units': 'metric', 'lang': "ru", 'APPID': key})
    data = resp.json()
    if data.get("count", 0) == 0:
        return "City not found!"
    else:
        wd = data['list'][0]
        return """
        Temp: {} *C
        Wind: {} m/s dir: {} *
        Rain: {}
        Snow: {}
        Clouds: {} %
        Description: {}
        """.format(wd["main"]["temp"], str(wd["wind"]["speed"]), str(wd["wind"]["deg"]), wd["rain"], wd["snow"],
                   wd["clouds"]["all"], wd["weather"][0]["description"])
