import json
import time

from functions import *
from selenium.webdriver.chrome.options import Options  # => 引入Chrome的配置
# from selenium.webdriver import ChromeOptions
from selenium import webdriver
import os
from selenium.webdriver.chrome.service import Service


def Chrome_Config(Chrome_path):
    service = Service(executable_path=Chrome_path)
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument("--headless")  # => 为Chrome配置无头模式
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def filter_cookie(cookie):
    cookie_dict = {
        'name': cookie['name'],
        'value': cookie['value'],
        'domain': cookie['domain'],
        'path': cookie['path'],
        'secure': cookie['secure'],
        'httpOnly': cookie['httpOnly'],
        'expiry': int(cookie['expirationDate']),
        'sameSite': "None" if cookie.get("sameSite") not in ["Strict", "Lax", "None"] else cookie["sameSite"]
    }
    return cookie_dict

if __name__ == '__main__':
    print("driver init...")
    driver = Chrome_Config("chromedriver.exe")  # In this function, you can config your chrome driver
    with open('cookies/fishcliptail.json', 'r') as cookies_file:
        cookies = json.load(cookies_file)
    driver.get('https://twitter.com/login')
    time.sleep(5)
    for cookie in cookies:
        try:
            cookie_dict = filter_cookie(cookie)
            driver.add_cookie(cookie_dict)
        except Exception as e:
            print(cookie['name'], e)
    while True:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
        url_list = ['https://x.com/cliptailfish']
        for url in url_list:
            print('open url...')
            driver.get(url)
            time.sleep(5)
            print('点击评论')
            button_xpath = "//section/div/div/div//div[@aria-label]/div[1]/button[@aria-label]"
            reply_button = driver.find_element(By.XPATH, button_xpath)
            reply_button.click()
            time.sleep(3)
            print('输入评论')
            # 等待可编辑区域加载完成
            editable_div_xpath = "//*[@data-testid='tweetTextarea_0']"
            editable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, editable_div_xpath))
            )
            # 聚焦元素
            editable_div.send_keys(Keys.CONTROL, "a")  # 选中编辑区域内的所有文本
            editable_div.send_keys(Keys.BACK_SPACE)  # 清除编辑区域内的所有文本
            # 输入文本
            tweet_text = "Hello World! This is an auto-filled tweet."
            editable_div.send_keys(tweet_text)
            time.sleep(3)
            print('点击发帖')
            button_xpath = '//div[@data-testid="toolBar"]/div/button[@data-testid="tweetButton"]'
            reply_button = driver.find_element(By.XPATH, button_xpath)
            reply_button.click()
            time.sleep(5)
        time.sleep(30)
