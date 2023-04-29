import urllib.request
import re
import aiohttp
import simplematrixbotlib as botlib
from bs4 import BeautifulSoup
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException

creds = botlib.Creds("https://homeserver", "username", "password")
bot = botlib.Bot(creds)
PREFIX = "!"

translating = False
url = "https://index.minfin.com.ua/ua/russian-invading/casualties/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # NOQA: E501
swearwords = list(map(lambda x: re.compile(x, re.IGNORECASE), [
    r'(^|\s)мля(\S*)',
    r'(^|\s)(б|6)ля(\S*)',
    r'(\S*)ъ(е|e)(б|6)(\S*)',
    r'(\S*)ж(о|o|0)(п|n)(\S*)',
    r'(^|\s)и(п|n)(а|a)т(\S*)',
    r'(^|\s)(е|e|ё)(п|n)т(\S*)',
    r'(^|\s)и(п|n)(е|e)т(\s|$)',
    r'(^|\s)ии(п|n)(е|e)т(\s|$)',
    r'(^|\s)(х|x)(е|e)(р|p)(\S*)',
    r'(^|\s)и(п|n)(а|a)(л|ть)(\S*)',
    r'(\S*)м(у|y)д(о|а|o|a|@)(\S*)',
    r'(\S*)пид(а|о|o|a|@)(р|p)(\S*)',
    r'(^|\s)д(р|p)(о|o|0)(ч|4)(\S*)',
    r'(^|\s)(с|c)(у|y)(к|k)(а|a)(\S*)',
    r'(\S*)(х|x)(у|y)(й|и|я|е|e)(\S*)',
    r'(\S*)г(а|о|0|o|a)нд(0|о|o)н(\S*)',
    r'(^|\s)(з|3)(а|a)л(у|y)(п|n)(\S*)',
    r'(^|\s)(е|ё|e)(б|6)(а|a)(p|р)(\S*)',
    r'(^|\s)(а|о)к(у|y)(е|e)нн(а|о)(\S*)',
    r'(\S*)(е|e)(б|6)(а|@)(т|н|t|h)(\S*)',
    r'(^|\s)(с|c)(р|p)(а|a)(к|т|k|t)(\S*)',
    r'(^|\s)(n|п)(о|o|0)(x|х)(e|е)(p|р)(\S*)',
    r'(^|\s)(п|n)(и|e|е)(с|c|з|3)д(а|a)(\S*)',
    r'(^|\s)(с|c|3|з)(а|a)(е|e)пи(с|c)ь(\s|$)'
    r'(^|\s)(n|п)(o|0|о)(е|e)(б|6)(е|e)н(ь|ъ)(\s|$)',
    r'(\S*)(п(и|e|е)|3\.14)(з|3|c|с)(д|т)(а|a|e|е)(\S*)',
]))


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
            return response_json


def vova_yibash():
    try:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})  # NOQA: E501
        html_page = urllib.request.urlopen(request)
        soup = BeautifulSoup(html_page, "html.parser")
        casualties_div = soup.find("div", {"class": "casualties"})
        li_elements = casualties_div.find_all("li")
        casualties_list = []
        for li in li_elements:
            casualties_list.append(li.text)
        return casualties_list
    except Exception as e:
        print(f"Error in vova_yibash: {e}")
        return []


@bot.listener.on_message_event
async def femboj(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("фембой") or match.command("femboj")):  # NOQA: E501
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api.catboys.com/img") as response:  # NOQA: E501
                    data = await response.json()
                    await bot.api.send_text_message(room.room_id, data["url"])
            except Exception as e:
                print(f"Error in femboj: {e}")


@bot.listener.on_message_event
async def translate(room, message):
    global translating
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("переклади") or match.command("perekladu")):  # NOQA: E501
        if translating:
            return
        else:
            translating = True
        try:
            language = match.args()[0]
            text = "+".join(arg for arg in match.args()[1:])
            url = f"https://simplytranslate.pussthecat.org/api/translate/?engine=google&to={language}&text={text}"  # NOQA: E501
            response_json = await fetch_data(url)

            await bot.api.send_text_message(room.room_id, response_json["translated-text"])  # NOQA: E501
        except Exception as e:
            print(f"Error in translate: {e}")
        finally:
            translating = False


@bot.listener.on_message_event
async def rusnya(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("русня") or match.command("rusnya")):  # NOQA: E501
        try:
            casualties_list = vova_yibash()
            casualties_str = "\n".join(casualties_list)
            await bot.api.send_text_message(room.room_id, casualties_str)
        except Exception as e:
            print(f"Error in rusnya: {e}")


@bot.listener.on_message_event
async def calculator(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("підрахуй") or match.command("pidrahuj")):  # NOQA: E501
        try:
            expression = " ".join(match.args())
            allowed_chars = set("0123456789+-*/() ")
            if set(expression) - allowed_chars:
                raise ValueError("Заборонені символи")
            result = eval(expression)
            await bot.api.send_text_message(room.room_id, f"{expression} = {result}")  # NOQA: E501
        except Exception as e:
            print(f"Error in calculator:\nInvalid expression: '{expression}'. Reason:\n{e}")  # NOQA: E501
            await bot.api.send_text_message(room.room_id, f"помилка виконання операції {expression}")  # NOQA: E501


@bot.listener.on_message_event
async def rusnyava_mova(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot():
        message = " ".join(match.args())
        filtered = ' '.join([w for w in match.args() if not any([sw.search(w) for sw in swearwords])])  # NOQA: E501
        try:
            for result in detect_langs(filtered):
                if result.lang == 'ru' and result.prob > 0.9:
                    await bot.api.send_text_message(room.room_id, "адмін, русня у чаті")  # NOQA: E501
        except LangDetectException as e:
            print(f"Error in rusnyava_mova:\nCan't detect lang in message: '{message}'. Reason:\n{e}")  # NOQA: E501

bot.run()
