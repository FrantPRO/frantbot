import datetime
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


def wind_direction(grad: int) -> str:
    if 0 <= grad < 22.5:
        return "nord"
    elif 22.5 <= grad < 67.5:
        return "norf-east"
    elif 67.5 <= grad < 112.5:
        return "east"
    elif 112.5 <= grad < 157.5:
        return "south-east"
    elif 157.5 <= grad < 202.5:
        return "south"
    elif 202.5 <= grad < 247.5:
        return "south-west"
    elif 247.5 <= grad < 292.5:
        return "west"
    elif 292.5 <= grad < 337.5:
        return "north-west"
    elif 337.5 <= grad <= 380:
        return "nord"


def weather_forecast(city, weather_key, timezone_key):
    city = city.replace("-", " ").replace("  ", " ").strip()
    resp = requests.get("https://api.openweathermap.org/data/2.5/find",
                        params={'q': city, 'units': 'metric', 'lang': "en", 'APPID': weather_key})
    data = resp.json()
    res = ""
    if data.get("count", 0) == 0:
        res = "{} not found!".format(city)
    else:
        for city_data in data['list']:

            resp_cur_time = requests.get("http://api.timezonedb.com/v2.1/get-time-zone?"
                                         "key={key}&format=json&by=position&"
                                         "lat={lat}&lng={lon}"
                                         .format(key=timezone_key, lat=city_data["coord"]["lat"],
                                                 lon=city_data["coord"]["lon"]))
            cur_time = resp_cur_time.json()

            res += "* {city} {country}\n" \
                   "geo: [{coord}]\n" \
                   "{date}\n" \
                   "Temp: {temp} *C\n" \
                   "Wind: {wind} m/s {wind_dir}\n" \
                   "Rain: {rain}\n" \
                   "Snow: {snow}\n" \
                   "Clouds: {clouds} %\n" \
                   "Description: {desc}" \
                .format(city=city_data["name"],
                        country=city_data["sys"]["country"],
                        coord=str(city_data["coord"]["lon"]) + ", " + str(city_data["coord"]["lat"]),
                        date=datetime.datetime.fromtimestamp(cur_time.get("timestamp", 0)).strftime("%d.%m.%Y %H:%M"),
                        temp=round(city_data["main"]["temp"]),
                        wind=str(city_data["wind"]["speed"]),
                        wind_dir=wind_direction(city_data["wind"]["deg"]),
                        rain=city_data["rain"],
                        snow=city_data["snow"],
                        clouds=city_data["clouds"]["all"],
                        desc=city_data["weather"][0]["description"])
    return res
