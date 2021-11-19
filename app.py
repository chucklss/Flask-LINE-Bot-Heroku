import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import time

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # catch incoming message text
    get_message = event.message.text

    # py2line(f'The message is {get_message}')

    if get_message.startswith('http'):
        reply = TextSendMessage(text="Thus URL is valid!!")
        # py2line(f'The message is {get_message}, 123')
    else:
        reply = TextSendMessage(text="This string is invalid...")
        # py2line(f'The message is {get_message}, 456')
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)
    line_bot_api.reply_message(event.reply_token, reply)

    # scrape url
    # reply = TextSendMessage(text=f"Starting to fetch from: \n{get_message}")
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)
    # line_bot_api.reply_message(event.reply_token, reply)
    py2line('Initializing Extraction...')
    url_message = url_extraction_RPA_heroku(get_message)
    py2line('Extraction Finished...')

    # Send To Line
    # reply = TextSendMessage(text=f"{url_message}")
    reply = TextSendMessage(text=f"Fetched URL: \n{url_message}")
    line_bot_api.reply_message(event.reply_token, reply)


def url_extraction_RPA_heroku(target_url):

    py2line('Entering RPA Process...')
    # step 0) browser setup
    # set path: chromdriver
    # path_driver = './chromedriver.exe'
    # set path: Brave browser
    # path_brave = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

    # create options-carrier
    # reply = TextSendMessage(text="Opening up Chrome...")
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)
    options = webdriver.ChromeOptions()

    # set browser application location
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # set browser arguments
    # options.add_argument('--incognito')  # incognito mode
    # options.add_argument('--disable-notifications')  # disable notifications
    # https://github.com/heroku/heroku-buildpack-google-chrome
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-proxy-server')
    options.add_argument("--proxy-server='direct://'");
    options.add_argument("--proxy-bypass-list=*");

    # open browser
    py2line('Opening Chrome...')
    browser = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options = options)

    # step 1) go to certain website
    # reply = TextSendMessage(text="Going to URL...")
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)
    py2line('Going to URL...')
    url = target_url.strip(' ').strip(',')
    py2line(f'Target URL:\n{url}')
    browser.get(target_url)

    # step 2) extract video name
    vid_name = browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/h1').text

    # step 3) extract video url
    frame = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/div[4]/iframe')
    browser.switch_to.frame(frame)
    element = browser.find_element_by_css_selector("#_iframe_content > center > button")
    element.click()

    # element = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/div[3]/div[1]')
    # element.click()
    
    while True:
        temp = browser.find_elements_by_xpath('//*[@id="kt_player"]/div[2]/div[1]/div[5]/div[2]')
        time.sleep(5)
        if len(temp) > 0:
            break

    # reply = TextSendMessage(text="Waiting Complete...")
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)

    browser.execute_script('document.getElementsByTagName("video")[0].pause()')
    vid_url = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/video')
    vid_url = vid_url.get_attribute('src')

    # reply = TextSendMessage(text="URL fetched...")
    # line_bot_api.push_message('U40afe82f0e8bd295d94c68f6c03c985f', reply)

    py2line(f'\n網址:\n{vid_url}\n名稱:{vid_name}')

    browser.quit()

    return vid_url

# set token: 烤秋芹啦
# main function
# define function:
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

def py2line(msg, token = 'WDXqcwrhMAYxVzU9DbAzLwWzuLbKFzBgWk20YvNi0OP'):
    lineNotifyMessage(token, msg)