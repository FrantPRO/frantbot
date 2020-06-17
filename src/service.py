import logging
import datetime
import requests
import xml.dom.minidom
import html.parser
import urllib.request
import urllib.parse
import re
from langdetect import detect
from math import ceil

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
            return {
                "currency": currency_code,
                "name": name,
                "date": date,
                "value": rate,
            }


def transliterate_text(text):
    result = ""
    dic = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "scz",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "u",
        "я": "ja",
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "zh",
        "З": "z",
        "И": "i",
        "Й": "i",
        "К": "k",
        "Л": "l",
        "М": "m",
        "Н": "n",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Scz",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "U",
        "Я": "Ya",
    }
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
    agent = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR "
        "2.0.50727; .NET CLR 3.0.04506.30)"
    }
    request = urllib.request.Request(link, headers=agent)
    raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="t0">(.*?)<'
    re_result = re.findall(expr, data)
    if len(re_result) == 0:
        result = "I can't translate this, sorry!"
    else:
        result = html.unescape(
            "Translation {in_text_lg} > {out_text_lg}\n"
            "{out_text}"
            .format(
                in_text_lg=from_language, out_text_lg=to_language, out_text=re_result[0]
            )
        )
    return result


def detect_lang(text):
    return detect(text)


def wind_direction(deg: int) -> str:
    directions = {
        1: "north",
        2: "north-east",
        3: "east",
        4: "south-east",
        5: "south",
        6: "south-west",
        7: "west",
        8: "north-west",
        9: "north",
    }
    return directions.get(
        ceil(((deg - (360 * int(deg / 360)) if deg > 360 else deg) + 22.5) / 45)
    )


def weather_forecast(city, weather_key, timezone_key):
    city_prep = city.replace("-", " ").replace("  ", " ").strip()
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/find",
        params={"q": city_prep, "units": "metric", "lang": "en", "APPID": weather_key}
    )
    data = resp.json()
    res = ""
    if data.get("count", 0) == 0:
        res = "{} not found!".format(city)
    else:
        for city_data in data.get("list", {}):

            coord = city_data.get("coord")
            if not coord:
                continue

            lat = coord.get("lat")
            lon = coord.get("lon")
            if not lat or not lon:
                continue

            resp_time = requests.get(
                "http://api.timezonedb.com/v2.1/get-time-zone?key={key}&format=json&by=position&"
                "lat={lat}&lng={lon}".format(key=timezone_key, lat=lat, lon=lon)
            )
            try:
                resp_cur_time = resp_time.json()
            except Exception as e:
                print("Error", {
                    "params": {
                        "lat": lat,
                        "lon": lon,
                        "resp_time": resp_time
                    },
                    "error": e
                })
                return "Not found"

            if resp_cur_time.get("status") != "OK":
                raise Exception(resp_cur_time.get("message"))

            cur_datatime = datetime.datetime.fromtimestamp(
                resp_cur_time.get("timestamp", 0)
            )
            cur_date = cur_datatime.strftime("%d.%m.%Y")
            cur_time = cur_datatime.strftime("%H:%M")

            if res:
                res += "\n\n"

            res += (
                "<b>{city} {country}</b>\n"
                '<a href="{coord_link}">geo: [{lat}, {lot}]</a>\n'
                "<em>Now</em> {date} <b>{time}</b>\n"
                "<em>Temp:</em> {temp} *C\n"
                "<em>Wind:</em> {wind} m/s {wind_dir}\n"
                "<em>Rain:</em> {rain}\n"
                "<em>Snow:</em> {snow}\n"
                "<em>Clouds:</em> {clouds} %\n"
                "<em>Description:</em> {desc}".format(
                    city=city_data["name"],
                    country=city_data["sys"]["country"],
                    coord_link="https://www.google.com/maps/@{lat},{lon},10z".format(
                        lat=str(city_data["coord"]["lat"]),
                        lon=str(city_data["coord"]["lon"]),
                    ),
                    lat=str(city_data["coord"]["lat"]),
                    lot=str(city_data["coord"]["lon"]),
                    date=cur_date,
                    time=cur_time,
                    temp=round(city_data["main"]["temp"]),
                    wind=str(city_data["wind"]["speed"]),
                    wind_dir=wind_direction(city_data["wind"]["deg"]),
                    rain=city_data["rain"],
                    snow=city_data["snow"],
                    clouds=city_data["clouds"]["all"],
                    desc=city_data["weather"][0]["description"]
                )
            )
    return res
