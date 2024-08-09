import json
import time

import config
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

def load_data():
    print('load data...')
    # 加载 cookies
    for name in os.listdir('cookies'):
        if name == config.COOKIES_NAME:
            with open(f'cookies/{name}', 'r') as file:
                cookies = json.load(file)
                break
    # 加载 users
    for name in os.listdir('users'):
        if name == config.USERS_NAME:
            with open(f'users/{name}', 'r') as file:
                users = [x.strip() for x in file.readlines()[config.USERS_RANGE[0]:config.USERS_RANGE[1]]]
                latelys = [None for _ in range(len(users))]
                break
    # 加载 comments
    for name in os.listdir('comments'):
        if name == config.COMMENTS_NAME:
            with open(f'comments/{name}', 'r', encoding='utf-8') as file:
                comments = [x.strip() for x in file.readlines()]
                break
    return cookies, users, comments, latelys
from dateutil import parser
from selenium.webdriver.common.by import By
from datetime import datetime
if __name__ == '__main__':
    print("driver init...")
    driver = Chrome_Config("chromedriver.exe")  # In this function, you can config your chrome driver
    # 加载数据
    cookies, users, comments, latelys = load_data()
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
        for i, url in enumerate(users):
            try:
                print('open url...', url)
                driver.get(url)
                time.sleep(5)

                # 假设 driver 已经是一个初始化好的 WebDriver 实例
                element_xpath = '//time'

                # 使用 find_element 和 By.XPATH 获取元素
                element = driver.find_element(By.XPATH, element_xpath)

                # 获取元素的 datetime 属性
                datetime_str = element.get_attribute('datetime')
                print('datetime_str', datetime_str)

                date_string = datetime_str

                # 使用 dateutil 解析字符串为 datetime 对象
                post_datetime = parser.parse(date_string)

                # 获取当前时间的 datetime 对象，这里使用 datetime.now() 获取当前本地时间
                # 如果需要 UTC 时间，可以使用 datetime.utcnow() 并确保它有时区信息
                current_datetime = datetime.now(datetime.now().astimezone().tzinfo)

                # 确保两个 datetime 对象都是 "aware" 并具有相同的时区
                # 这里我们使用 post_datetime 的时区信息
                current_datetime = current_datetime.astimezone(post_datetime.tzinfo)

                # 计算两个 datetime 对象之间的差异
                delta = current_datetime - post_datetime

                # 将差异转换为小时
                hours_difference = delta.total_seconds() / 3600

                print(f"相差小时数: {hours_difference:.2f}")

                if hours_difference > 1:
                    continue
                print('点击评论')
                button_xpath = "//section/div/div/div//div[@aria-label]/div[1]/button[@aria-label]"
                reply_button = driver.find_element(By.XPATH, button_xpath)
                reply_button.click()
                time.sleep(3)
                comment = comments[i % len(comments)]
                print('输入评论', comment)
                # 等待可编辑区域加载完成
                editable_div_xpath = "//*[@data-testid='tweetTextarea_0']"
                editable_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, editable_div_xpath))
                )
                # 聚焦元素
                editable_div.send_keys(Keys.CONTROL, "a")  # 选中编辑区域内的所有文本
                editable_div.send_keys(Keys.BACK_SPACE)  # 清除编辑区域内的所有文本
                # 输入文本
                script = f"""
                const editableDiv = document.querySelector('[data-testid="tweetTextarea_0"]');
                editableDiv.focus();
                document.execCommand('insertHTML', false, '{comment}');
                """
                driver.execute_script(script)
                time.sleep(3)
                print('点击发帖')
                button_xpath = '//div[@data-testid="toolBar"]/div/button[@data-testid="tweetButton"]'
                reply_button = driver.find_element(By.XPATH, button_xpath)
                reply_button.click()
                time.sleep(5)
            except Exception as e:
                print('error', e)
        time.sleep(10*60)
