
from typing import Union, List
import requests
from telegram import InlineKeyboardMarkup, KeyboardButton, MenuButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, CallbackQueryHandler
import os
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from PIL import Image
load_dotenv()


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

token = os.getenv('TOKEN')

base_url = "https://castbox.fm"


def download_files(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(
        executable_path="/usr/bin/chromedriver"), options=options)

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    numberOfEpisodes = soup.find(class_="trackListCon_title").string

    podcastTitle = driver.title

    dataToScrap = []
    episodes = soup.find_all(class_="episodeRow")
    dl_path = "podcasts/" + podcastTitle.replace(" ", "_")
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)

    for episode in episodes:
        # print(episode)
        imagepath = dl_path + "/" + episode.find('p')['title'] + ".jpg"
        if not os.path.isfile(imagepath):
            dl = requests.get(episode.find("img")["src"])
            with open(imagepath, "wb") as f:
                f.write(dl.content)

        item = {
            "link": episode.find('a')['href'],
            "title": episode.find('p')['title'],
            "duration": episode.find(class_="item icon time").string,
            "imageLink": episode.find("img")["src"],
            "imagePath": imagepath
        }

        dataToScrap.append(item)
        # print(item)

    mp3s = []
    for idx, episode in enumerate(dataToScrap):
        driver.get(base_url+episode["link"])

        episode_file = driver.find_element(
            By.TAG_NAME, 'source').get_attribute('src')

        dataToScrap[idx]["mp3Link"] = episode_file
        mp3s.append(episode_file)

        # download
        filepath = dl_path + "/" + episode["title"] + ".mp3"
        dataToScrap[idx]["filepath"] = filepath
        if not os.path.isfile(filepath):
            dl = requests.get(episode_file)
            with open(filepath, "wb") as f:
                f.write(dl.content)

    return dataToScrap, podcastTitle
    # print(episode_file)


def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int,
    header_buttons: Union[InlineKeyboardButton,
                          List[InlineKeyboardButton]] = None,
    footer_buttons: Union[InlineKeyboardButton,
                          List[InlineKeyboardButton]] = None
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(
            header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(
            footer_buttons, list) else [footer_buttons])
    return menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.from_user.first_name

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello "+name+".\nI'm a bot created by @NabidaM for downloading podcasts from castbox!\nSend me the link of the channel!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if base_url in text:
        await update.message.reply_text("fetching files...!\nPlease wait, the process can take a few minutes.")
        episodes, podcastTitle = download_files(text)
        await update.message.reply_text(f"Downloading {podcastTitle}.\nThis channel has {len(episodes)} episode(s)")

        for episode in episodes:
            f = open(episode["filepath"], "rb")
            thumbnail_file = open(episode["imagePath"], "rb")
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=f, caption=podcastTitle + " - " + episode["title"], title=episode["title"], thumb=thumbnail_file)

    else:
        await update.message.reply_text("send a valid url!")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Just send the castbox channel link to me :)")

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(echo_handler)

    # application.add_handler(CallbackQueryHandler(download_button))

    application.run_polling()
