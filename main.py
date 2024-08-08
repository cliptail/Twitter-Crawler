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
    print('open url...')
    driver.get('https://x.com/home')
    time.sleep(5)
    if driver.find_elements_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/nav/div/div[2]/div/div[2]/a'):
        print("登录成功！")
    else:
        print("可能未成功登录")
    driver.quit()
