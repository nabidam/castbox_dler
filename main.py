import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

base_url = "https://castbox.fm"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver = webdriver.Chrome(service=Service(executable_path="/usr/bin/chromedriver"), options=options)

#url = 'https://castbox.fm/channel/%DA%A9%D8%AA%D8%A7%D8%A8-%D8%B5%D9%88%D8%AA%DB%8C-%D9%88%D9%82%D8%AA%DB%8C-%D9%86%DB%8C%DA%86%D9%87-%DA%AF%D8%B1%DB%8C%D8%B3%D8%AA-id5163915?country=us'
# url = "https://castbox.fm/channel/Radio-chehrazi---%D8%B1%D8%A7%D8%AF%DB%8C%D9%88-%DA%86%D9%87%D8%B1%D8%A7%D8%B2%DB%8C-id2015353?country=us"
url = "https://castbox.fm/va/5163915"

driver.get(url)

soup = BeautifulSoup(driver.page_source, 'html.parser')

numberOfEpisodes = soup.find(class_="trackListCon_title").string
podcastTitle = driver.title

dataToScrap = []
episodes = soup.find_all(class_="episodeRow")
for episode in episodes:
    print(episode)
    item = {
        "link": episode.find('a')['href'],
        "title": episode.find('p')['title'],
        "duration": episode.find(class_="item icon time").string,
        "imageLink": episode.find("img")["src"] 
    }

    dataToScrap.append(item)
    print(item)

dl_path = "podcasts/" + podcastTitle.replace(" ", "_")
if not os.path.exists(dl_path):
    os.makedirs(dl_path)

mp3s = []
for idx, episode in enumerate(dataToScrap):
    driver.get(base_url+episode["link"])

    episode_file = driver.find_element(By.TAG_NAME, 'source').get_attribute('src')

    dataToScrap[idx]["mp3Link"] = episode_file
    mp3s.append(episode_file)
    
    # download
    filepath = dl_path + "/" + episode["title"] + ".mp3"
    if not os.path.isfile(filepath):
        dl = requests.get(episode_file)
        with open(filepath, "wb") as f:
            f.write(dl.content)

    print(episode_file)


# dl_path = "podcasts/" + podcastTitle.replace(" ", "_")
# if not os.path.exists(dl_path):
#     os.makedirs(dl_path)

# for episode in dataToScrap:
#     filepath = dl_path + "/" + episode["title"] + ".mp3"
#     if not os.path.isfile(filepath):
#         dl = requests.get(episode["mp3Link"])
#         with open(filepath, "wb") as f:
#             d.write(dl.content)

# print(dataToScrap)
# episode = driver.find_element(By.CLASS_NAME, 'episodeRow')

# print(episode)
# # print(episode.get_attribute())

# episodes = driver.find_elements(By.CSS_SELECTOR, '.episodeRow')

# print(episodes[0].text)
# print(episodes.get_attribute())
# driver.close()
