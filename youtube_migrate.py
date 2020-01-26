"""
Automatic migration of subscriptions to another
YouTube account with Python and Selenium.

Tested with:
 - selenium 3.0
 - chrome 79.0
 - python 3.5

 1. Install selenium from pypi:
    $ pip install selenium

 2. Go to the down of page https://www.youtube.com/subscription_manager
    and download your current subscriptions feed.
    Save file as subscription_manager.xml in current folder or update the runtime variable below
    
 3. Use the youtube api to fetch a list of likes with the attributes snippet and contentDetails.
    Save as likes.json in current folder or update the runtime variable below
 
 4. Create a new profile in chrome and login with your google account
 
 5. Copy the profile folder (found using chrome://version) and rename the folder to Default. 
    Place the folder in an empty parent folder and paste the parent folder's path in the variable below

 6. Run script and go to drink coffee.
    It will take some time.
"""

# Variables likely to need updating after youtube design changes
like_button_with_pressed_attribute = 'ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button button' #This button is not pressable and only contains an attribute that shows the video was already liked
like_button_to_press = 'ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button.style-text'
subscribe_button = '#subscribe-button'
youtube_video_url_base = 'https://www.youtube.com/watch?v='
youtube_channel_url_base = 'https://www.youtube.com/channel/'

from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from xml.dom import minidom
import json
import time
import re

# Runtime variables
likes_json_locaion = "./likes.json"
subscriptions_location = "./subscription_manager.xml"

def main():
    options = Options()
    options.add_argument("user-data-dir=C:\\Users\\Jesca\\Desktop\\youtube transfer\\profile")
    driver = webdriver.Chrome(options=options)
    transfer_subscribtions(driver)
    transfer_likes(driver)
    driver.close()
    
def transfer_likes(driver):
    for video_to_like in load_likes():
        like(driver, video_to_like)
        
        
def video_is_liked(driver):
    result = driver.find_element_by_css_selector(like_button_with_pressed_attribute).get_attribute("aria-pressed")
    return result=="true"
        

def like(driver, video):
    try:
        channel_url = youtube_video_url_base + video["id"]
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector(like_button_to_press)
        is_liked = video_is_liked(driver)
            
        if not is_liked:
            button.click()

        print('{:.<50}{}'.format(video["title"], 'skip' if is_liked else 'done'))
    except:
        print('{:.<50}{}'.format(video["title"], "Whoops! Something went wrong! Moving on!"))
    time.sleep(1)
    
def load_likes():
    input_file = open (likes_json_locaion)
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
    xmldoc = minidom.parse(subscriptions_location)
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
        channel_url = youtube_channel_url_base + channel.id
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector(subscribe_button)
        is_subscribed = button.get_attribute('data-is-subscribed')

        if not is_subscribed:
            button.click()

        print('{:.<50}{}'.format(channel.title, 'skip' if is_subscribed else 'done'))
    except:
        print('{:.<50}{}'.format(channel.title, "Whoops! Something went wrong! Moving on!"))
    time.sleep(1)


if __name__ == '__main__':
    main()
