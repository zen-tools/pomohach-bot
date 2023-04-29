import urllib.request
import re
import aiohttp
import simplematrixbotlib as botlib
from bs4 import BeautifulSoup
from langdetect import detect_langs

creds = botlib.Creds("https://homeserver", "username", "password")
bot = botlib.Bot(creds)
PREFIX = "!"

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
            return response_json


url = "https://index.minfin.com.ua/ua/russian-invading/casualties/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"


def vova_yibash():
    try:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
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


# calculator function
def calculate(expression):
    try:
        return eval(expression)
    except Exception:
        return "Invalid expression"


@bot.listener.on_message_event
async def femboj(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("фембой") or match.command("femboj")):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api.catboys.com/img") as response:
                    data = await response.json()
                    await bot.api.send_text_message(room.room_id, data["url"])
            except Exception as e:
                print(f"Error in femboj: {e}")


translating = False


@bot.listener.on_message_event
async def translate(room, message):
    global translating
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("переклади") or match.command("perekladu")):
        if translating:
            return
        else:
            translating = True
        try:
            language = match.args()[0]
            text = "+".join(arg for arg in match.args()[1:])
            url = f"https://simplytranslate.pussthecat.org/api/translate/?engine=google&to={language}&text={text}"
            response_json = await fetch_data(url)

            await bot.api.send_text_message(room.room_id, response_json["translated-text"])
        except Exception as e:
            print(f"Error in translate: {e}")
        finally:
            translating = False


@bot.listener.on_message_event
async def rusnya(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("русня") or match.command("rusnya")):
        try:
            casualties_list = vova_yibash()
            casualties_str = "\n".join(casualties_list)
            await bot.api.send_text_message(room.room_id, casualties_str)
        except Exception as e:
            print(f"Error in rusnya: {e}")


@bot.listener.on_message_event
async def calculator(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and (match.command("підрахуй") or match.command("pidrahuj")):
        try:
            expression = " ".join(match.args())
            allowed_chars = set("0123456789+-*/() ")
            if set(expression) - allowed_chars:
                raise ValueError("Заборонені символи")
            result = eval(expression)
            await bot.api.send_text_message(room.room_id, f"{expression} = {result}")
        except Exception as e:
            print(f"Error in calculator: {e}")
            await bot.api.send_text_message(room.room_id, f"помилка виконання операції {expression}")


@bot.listener.on_message_event
async def rusnyava_mova(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot():
        message = " ".join(match.args())
        print(message)
        try:
            results = detect_langs(message)
            for result in results:
                if result.lang == 'ru' and result.prob > 0.9:
                    await bot.api.send_text_message(room.room_id, "адмін, русня у чаті")
        except Exception as e:
            print(f"Error in rusnyava_mova: {e}")

bot.run()
