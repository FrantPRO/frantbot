import requests
import xml.dom.minidom

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
            return {"currency": currency_code, "name": name,"date": date, "value": rate}


def transliterate_text(text):
    result = ""
    dic = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
              "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
              "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h",
              "ц": "c", "ч": "cz", "ш": "sh", "щ": "scz", "ъ": "", "ы": "y", "ь": "", "э": "e",
              "ю": "u", "я": "ja", "А": "a", "Б": "b", "В": "v", "Г": "g", "Д": "d", "Е": "e", "Ё": "e",
              "Ж": "zh", "З": "z", "И": "i", "Й": "i", "К": "k", "Л": "l", "М": "m", "Н": "n",
              "О": "o", "П": "p", "Р": "r", "С": "s", "Т": "t", "У": "u", "Ф": "Х", "Х": "h",
              "Ц": "c", "Ч": "cz", "Ш": "sh", "Щ": "scz", "Ъ": "", "Ы": "y", "Ь": "", "Э": "e",
              "Ю": "u", "Я": "ja"}
    for i in range(len(text)):
        if text[i] in dic:
            sim = dic[text[i]]
        else:
            sim = text[i]
        result += sim
    return result
