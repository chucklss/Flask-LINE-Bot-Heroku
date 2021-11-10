### Module: LINE 串接
## Import Packages
import requests

## Define Function
# set token: 烤秋芹啦
token = 'WDXqcwrhMAYxVzU9DbAzLwWzuLbKFzBgWk20YvNi0OP'

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

def py2line(msg, token = token):
    lineNotifyMessage(token, msg)

### Module: URL Scrape
## Import Packages
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

## Define Function
def url_extraction_RPA(target_url):
	# step 0) browser setup
	# set path: chromdriver
    path_driver = './chromedriver.exe'
    # set path: Brave browser
    path_brave = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

    # create options-carrier
    options = webdriver.ChromeOptions()

    # set browser application location
    options.binary_location = path_brave
    # set browser arguments
    options.add_argument('--incognito')  # incognito mode
    options.add_argument('--disable-notifications')  # disable notifications

    # open browser
    browser = webdriver.Chrome(executable_path = path_driver, chrome_options = options)

    # step 1) go to certain website
    browser.get(target_url)

    # step 2) extract video name
    vid_name = browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/h1').text

    # step 3) extract video url
    frame = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/div[4]/iframe')
    browser.switch_to_frame(frame)
    element = browser.find_element_by_css_selector("#_iframe_content > center > button")
    element.click()

    # element = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/div[3]/div[1]')
    # element.click()
    
    while True:
        temp = browser.find_elements_by_xpath('//*[@id="kt_player"]/div[2]/div[1]/div[5]/div[2]')
        time.sleep(5)
        if len(temp) > 0:
            break
    browser.execute_script('document.getElementsByTagName("video")[0].pause()')
    vid_url = browser.find_element_by_xpath('//*[@id="kt_player"]/div[2]/video')
    vid_url = vid_url.get_attribute('src')

    py2line(f'\n網址:\n{vid_url}\n名稱:{vid_name}')

    browser.close()

### Module: Arguments Parser
## Import Packages
import argparse

## Define Argument Parser
def arg_parser():
    parser = argparse.ArgumentParser(description='TKtube Extraction')

    parser.add_argument("--URL", type=str, default="",
            help="Insert URL on the tk-tube webpage.")
    
    args = parser.parse_args()
    return args

### Module: Assembly of modules
if __name__  == '__main__':
    # parse args
    args = arg_parser()

    # main process
    url_extraction_RPA(target_url = args.URL)