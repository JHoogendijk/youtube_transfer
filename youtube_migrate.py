"""
Automatic migration of subscriptions to another
YouTube account with Python and Selenium.

Tested with:
 - selenium 3.0
 - firefox 49.0
 - python 3.5

 1. Install selenium from pypi:
    $ pip install selenium

 2. Go to the down of page https://www.youtube.com/subscription_manager
    and download your current subscriptions feed.
    Save file as subscription_manager.xml.

 4. Run script, enter your credentials and go to drink coffee.
    It will take some time.

Note YouTube will temporary block you if you have more that 80 subscriptions.
Just restart the script in a few hours.
"""

from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from xml.dom import minidom
import json
import time
import re


def main():
    options = Options()
    options.add_argument("user-data-dir=C:\\Users\\Jesca\\Desktop\\youtube transfer\\profile")
    driver = webdriver.Chrome(options=options)
    #transfer_subscribtions(driver)
    transfer_likes(driver)
    driver.close()
    
def transfer_likes(driver):
    for video_to_like in load_likes():
        like(driver, video_to_like)
        
        
def video_is_liked(driver):
    result = driver.find_element_by_css_selector('ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button button').get_attribute("aria-pressed")
    return result=="true"
        

def like(driver, video):
    try:
        channel_url = 'https://www.youtube.com/watch?v=' + video["id"]
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector('ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button.style-text')
        is_liked = video_is_liked(driver)
            
        if not is_liked:
            button.click()

        print('{:.<50}{}'.format(video["title"], 'skip' if is_liked else 'done'))
    except:
        print('{:.<50}{}'.format(video["title"], "Whoops! Something went wrong! Moving on!"))
    time.sleep(1)
    
def load_likes():
    input_file = open ('likes.json')
    json_array = json.load(input_file, encoding="utf8")
    videos_to_like = list()
    for like in reversed(json_array):
        video_to_like = dict()
        video_to_like["title"] = like["snippet"]["title"]
        video_to_like["id"] = like["contentDetails"]["videoId"]
        videos_to_like.append(video_to_like)
    return videos_to_like
    
    
def transfer_subscribtions(driver):
    for channel in load_subcribtions():
        subscribe(driver, channel)
     

def load_subcribtions():
    xmldoc = minidom.parse('subscription_manager.xml')
    itemlist = xmldoc.getElementsByTagName('outline')
    channel_id_regexp = re.compile('channel_id=(.*)$')
    Channel = namedtuple('Channel', ['id', 'title'])
    subscriptions = []

    for item in itemlist:
        try:
            feed_url = item.attributes['xmlUrl'].value
            channel = Channel(id=channel_id_regexp.findall(feed_url)[0],
                              title=item.attributes['title'].value)
            subscriptions.append(channel)
        except KeyError:
            pass

    return subscriptions


def subscribe(driver, channel):
    try:
        channel_url = 'https://www.youtube.com/channel/' + channel.id
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector('#subscribe-button')
        is_subscribed = button.get_attribute('data-is-subscribed')

        if not is_subscribed:
            button.click()

        print('{:.<50}{}'.format(channel.title, 'skip' if is_subscribed else 'done'))
    except:
        print('{:.<50}{}'.format(channel.title, "Whoops! Something went wrong! Moving on!"))
    time.sleep(1)


if __name__ == '__main__':
    main()
