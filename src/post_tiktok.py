import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
import json

emoji = "#amazon #amazonfinds #trouvailles"
def get_cookies(path: str) -> dict:
    """
    Gets cookies from the passed file using the netscape standard
    """
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n')

    return_cookies = []
    for line in lines:
        split = line.split('\t')
        if len(split) < 6:
            continue

        split = [x.strip() for x in split]

        try:
            split[4] = int(split[4])
        except ValueError:
            split[4] = None

        return_cookies.append({
            'name': split[5],
            'value': split[6],
            'domain': split[0],
            'path': split[2],
        })

        if split[4]:
            return_cookies[-1]['expiry'] = split[4]
    return return_cookies


def upload_tiktok(video_path, title_video=None, hashtags=""):
    # Créez un objet ChromeOptions pour personnaliser les options du navigateur
    userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={userAgent}')
    # options.add_argument('headless')
    options.add_experimental_option('extensionLoadTimeout', 60000)
    driver = webdriver.Chrome(options=options)

    cookies_list = get_cookies(r"C:\Users\armen\Documents\github\VidETL\assets\www.tiktok.com_cookies.txt")
    # print("cookies_list:", cookies_list)

    driver.get("https://tiktok.com")

    wait = WebDriverWait(driver, 60)

    print("tiktok.com chargé!")
    for cookie in cookies_list:
        driver.add_cookie(cookie)

    driver.refresh()

    print("cookies chargé!")

    wait = WebDriverWait(driver, 60)

    anchor_element = driver.find_element(By.XPATH, "//*[@id=\"app-header\"]/div/div[3]/div[1]/a")
    href_value = anchor_element.get_attribute('href')
    if href_value:
        driver.get(href_value)

        driver.refresh()
        print("je me dirige vers le header")

        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tiktok-cookie-banner')))
        # There is an iframe on the page...
        shadow_host = driver.find_element(By.CSS_SELECTOR, 'tiktok-cookie-banner')
        print("shadow_host:", shadow_host)
        shadow_root = shadow_host.shadow_root
        try:
            decline_buton = shadow_root.find_element(By.CSS_SELECTOR, ".tiktok-cookie-banner .button-wrapper button:nth-child(2)")
            decline_buton.click()
        except Exception as e:
            print("error", e)
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe')))
        iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
        driver.switch_to.frame(iframe)

        # Wait until page loads...
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        
        # Select the input file and send the filename...
        upload = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        upload.send_keys(video_path)
        print("J'upload la vidéo")
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mobile-preview-player")))
        print("la vidéo a terminé d'être chargé!")
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
        
        # Title
        list_of_hashtags = ["#amazon", "#amazon", "#gedgets", "#amazonmusthaves", "#tiktokmademebuyit"]
        title = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        WebDriverWait(driver, 60).until(lambda driver: title.text != '')
        title.send_keys(2 * len(title.text) * Keys.BACKSPACE)
        WebDriverWait(driver, 60).until(lambda driver: title.text == '')
        title.send_keys(title_video)
        time.sleep(3)
        for hashtag in list_of_hashtags:
            title.send_keys(hashtag)
            wait = WebDriverWait(driver, 60)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mentionSuggestions")))
            hashtags_list = driver.find_element(By.CSS_SELECTOR, ".mentionSuggestions")
            hashtags_list = hashtags_list.get_attribute("outerHTML")
            wait = WebDriverWait(driver, 60)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".hash-text")))
            found_hashtag = driver.find_element(By.CSS_SELECTOR, ".hash-text")
            found_hashtag.click()
            title.send_keys(Keys.SPACE)
            print("J'écris le titre:", title_video, "et je clique sur ce hashtag", hashtag)

        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-post button')))
        post_button = driver.find_element(By.CSS_SELECTOR, '.btn-post button')
        print("text",post_button.text)
        print("disabled:",post_button.get_attribute("disabled"))
        # Wait until the button is clickable...
        wait = WebDriverWait(driver, 60)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-post button')))
        print("text",post_button.text)
        print("disabled:",post_button.get_attribute("disabled"))
        # Cliquez sur l'élément qui masque la bannière
        # post_button.click()
        print("Je clique sur publier")
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tiktok-modal__modal-content')))
        with open("page_source.txt", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        # os.remove(video_path)
        print("Vidéo envoyé pour publication!")
        driver.quit()

upload_tiktok(r"C:\Users\armen\Documents\github\VidETL\innovgadgetspot_1\output.mp4", title_video=f"Les pépites amazon")