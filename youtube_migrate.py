"""
Automatic migration of subscriptions and likes to another
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
    
 6. Close all instances of chrome
    
 7. Run script and go to drink coffee.
    It will take some time.
"""

# Variables likely to need updating after youtube design changes
like_button_with_pressed_attribute = 'ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button button' #This button is not pressable and only contains an attribute that shows the video was already liked
like_button_to_press = 'ytd-toggle-button-renderer.style-scope.ytd-menu-renderer.force-icon-button.style-text'
subscribe_button = '#subscribe-button'
subscribe_button_text = subscribe_button + " paper-button"
youtube_video_url_base = 'https://www.youtube.com/watch?v='
youtube_channel_url_base = 'https://www.youtube.com/channel/'

from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from xml.dom import minidom
import json
import time
import re
import argparse
import pickle
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('--likes_location', '-ll', help='file containing the likes', type=str, default='./likes.json', dest='likes_location')
parser.add_argument('--subscriptions_location', '-sl', help='file containing the subscriptions', type=str, default='./subscription_manager.xml', dest='subscriptions_location')
parser.add_argument('--likes_done_location', '-ldl', help='file containing the likes already done', type=str, default='./likes_done', dest='likes_done_location')
parser.add_argument('--subscriptions_done_location', '-sdl', help='file containing the subscriptions already done', type=str, default='./subscriptions_done', dest='subscriptions_done_location')
parser.add_argument("--transfer_subscriptions", '-ts', type=bool, nargs='?',
                        const=True, default=False,
                        help="Add this argument to transfer subscriptions",
                        dest='transfer_subscriptions')
parser.add_argument("--transfer_likes", '-tl', type=bool, nargs='?',
                        const=True, default=False,
                        help="Add this argument to transfer likes",
                        dest='transfer_likes')
args = parser.parse_args()

# Runtime variables
likes_json_locaion = args.likes_location
subscriptions_location = args.subscriptions_location
do_subscriptions = args.transfer_subscriptions
do_likes = args.transfer_likes
likes_done_path = args.likes_done_location
subscriptions_done_path = args.subscriptions_done_location

def main():
    options = Options()
    options.add_argument("user-data-dir=C:\\Users\\Jesca\\Desktop\\youtube transfer\\profile")
    driver = webdriver.Chrome(options=options)
    if do_subscriptions:
        transfer_subscriptions(driver)
    if do_likes:
        transfer_likes(driver)
    driver.close()
    
def transfer_likes(driver):
    maybe_create_likes_done()
    likes_done = load_likes_done()
    videos_to_like = load_likes(likes_done)
    i = 0
    n = len(videos_to_like)
    for video_to_like in videos_to_like:
        i += 1
        likes_done = like(driver, video_to_like, likes_done, i, n)
        
def maybe_create_likes_done():
    exists = os.path.exists(likes_done_path)
    if not exists:
        with open(likes_done_path, 'wb') as fp:
            pickle.dump([], fp)
        
def load_likes_done():
    with open(likes_done_path, 'rb') as fp:
        return pickle.load(fp)
        
def save_like_done(likes_done):
    with open(likes_done_path, 'wb') as fp:
        pickle.dump(likes_done, fp)
        
def video_is_liked(driver):
    result = driver.find_element_by_css_selector(like_button_with_pressed_attribute).get_attribute("aria-pressed")
    return result=="true"

def like(driver, video, likes_done, i, n):
    try:
        channel_url = youtube_video_url_base + video["id"]
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector(like_button_to_press)
        is_liked = video_is_liked(driver)
            
        if not is_liked:
            button.click()
        
        likes_done.append(video["id"])
        save_like_done(likes_done)
        print('{:.<70}{}'.format(video["title"][:67], 'skip' + '(' + str(i) + '/'+ str(n) + ')' if is_liked else 'done' + '(' + str(i) + '/'+ str(n) + ')'))
    except:
        print('{:.<70}{}'.format(video["title"][:67], "Whoops! Something went wrong! Moving on!" + '(' + str(i) + '/'+ str(n) + ')'))
    time.sleep(1)
    return likes_done
    
def load_likes(likes_done):
    input_file = open (likes_json_locaion)
    json_array = json.load(input_file, encoding="utf8")
    videos_to_like = list()
    for like in reversed(json_array):
        video_to_like = dict()
        video_to_like["title"] = like["snippet"]["title"]
        video_to_like["id"] = like["contentDetails"]["videoId"]
        if (not video_to_like["id"] in likes_done) and (not video_to_like["title"] == "Private video"):
            videos_to_like.append(video_to_like)
    return videos_to_like
    
    
def transfer_subscriptions(driver):
    maybe_create_likes_done()
    subscriptions_done = load_subscriptions_done()
    subscriptions = load_subcriptions(subscriptions_done)
    n = len(subscriptions)
    i = 0
    for channel in subscriptions:
        i += 1
        subscriptions_done = subscribe(driver, channel, subscriptions_done, i, n)
     

def load_subcriptions():
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
        
def maybe_create_subscriptions_done():
    exists = os.path.exists(subscriptions_done_path)
    if not exists:
        with open(subscriptions_done_path, 'wb') as fp:
            pickle.dump([], fp)
        
def load_subscriptions_done():
    with open(subscriptions_done_path, 'rb') as fp:
        return pickle.load(fp)
        
def save_subscriptions_done(subscriptions_done):
    with open(subscriptions_done_path, 'wb') as fp:
        pickle.dump(subscriptions_done, fp)

def subscribe(driver, channel, subscriptions_done, i, n):
    try:
        channel_url = youtube_channel_url_base + channel.id
        driver.get(channel_url)
        time.sleep(1)

        button = driver.find_element_by_css_selector(subscribe_button)
        is_subscribed = driver.find_element_by_css_selector(subscribe_button_text).get_attribute("subscribed")

        if not is_subscribed:
            button.click()

        if (not channel.id in likes_done):
            subscriptions_done.append(video_to_like)
        print('{:.<70}{}'.format(channel.title[:67], 'skip' + '(' + str(i) + '/'+ str(n) + ')' if is_subscribed else 'done' + '(' + str(i) + '/'+ str(n) + ')'))
    except:
        print('{:.<70}{}'.format(channel.title[:67], "Whoops! Something went wrong! Moving on!" + '(' + str(i) + '/'+ str(n) + ')'))
    time.sleep(1)
    return subscriptions_done


if __name__ == '__main__':
    main()
