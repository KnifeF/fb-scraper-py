import os
import codecs
# import pyautogui
# import pyscreenshot
# from time import sleep
from datetime import datetime
# from random import randint

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


ABC_STR = 'abcdefghijklmnopqrstuvwxyz'
# ****************************************GUI Constants*********************************************
# GUI Title and Images
GUI_TITLE = "Facebook Crawler"
IMG_PATH = r'fb_img.png'
ICO_PATH = r'target-focus.ico'

# Labels and buttons for GUI
OPEN_L = "Open..."
FILE_L = "File"
CLEAR_L = "Clear Text"
EXIT_L = 'Exit'
SAVE_L = "Save"
HELP_L = "Help"
ABOUT_L = 'About...'
CONVERT_L = "Convert To UIDs"
HOW_TO_CONVERT_USES = "How to convert FB users to ids?"
CONVERT_USERS = "Convert FB users to ids!"
ENTER_TARGETS = "Please Enter Your Facebook Targets (Users' IDS): "
Q_NOTE = "* Runs On facebook's mobile version (JavaScript disabled)"
# Check Buttons for GUI
ALL_CHK_BUTTONS = [["Groups", "Pages' liked", "Friends", "Followers"],
                   ["Stories' liked", "Photos' liked", "Videos' liked", "Stories' commented"],
                   ["Photos' commented", "Videos' commented", "Apps", "Screenshots"],
                   ["*Posts", "*About", "Exist On Facebook?", "Download Profile Pictures"],
                   ['Google Reverse Image Search', 'Tineye Reverse Image Search'],
                   ['Check On Each Profile', 'Compare Between All profiles']]
QUIT_BUTTON = 'Quit'
START_BUTTON = 'Start Crawling'

# GUI Instructions
CRAWLER_INSTRUCTIONS = "Enter a list* of profiles to crawl, or open a text file with a list of profiles.\n" + \
                               "Then, click on the desired options to crawl, and click 'start crawling'\n" + \
                               "to start the collection from facebook.\n\n"+"* Hit 'Enter' between each user, e.g:\n\n" + \
                               "100001234567\n"+"10000054321"
USR_TO_ID_INSTRUCTIONS = "Enter a list* of users, or open a text file with a list of users.\nThen," \
                         " click on 'Convert FB users to ids!', to convert the desired users\n" \
                         "to facebook ids. The crawler will run and return the ids..\n\n" \
                         "* Hit 'Enter' between each user, e.g:\n\njohn.55\nmolly6\n"

# Used for IO and FileDialog
TXT_TYPE = (("text files", "*.txt"), )

# Fonts and colors
LUCIDA = "Lucida Grande"
BOLD = 'bold'
UNDER_L = 'underline'
ITALIC = 'italic'
BLACK = 'black'
WHITE = 'white'
RED = 'red'

# ****************************************WebDriver Settings / parameters***************************************
WITHOUT_EXTENSIONS = "--disable-extensions"
PREFERENCES = {'profile.managed_default_content_settings.javascript': 2}  # Disable JavaScript From Browser
ARGUMENTS = r'user-data-dir='+os.path.join(os.environ["HOMEPATH"], r'AppData\Local\Google\Chrome\User Data')  # Use Cookies
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')
PREFERENCES_PATH = os.path.join(os.environ["HOMEPATH"], r'AppData\Local\Google\Chrome\User Data\Default')
PROXIES_SITE = "https://free-proxy-list.net/"
INTEL_TECHNIQUES = "https://inteltechniques.com/"
# ****************************************Facebook URLS and queries*********************************************
FACEBOOK = "https://www.facebook.com/"
MOBILE_FACEBOOK = "https://mbasic.facebook.com/"
MOBILE_FACEBOOK2 = "https://m.facebook.com"  # In case 'FB_URL2' is not working for - facebook no JS version
FACEBOOK_SEARCH = FACEBOOK+"search"
FID_QUERY = "/[fid]/"
BASE_PROFILE_URL = FACEBOOK+FID_QUERY.strip('/')
BASE_PROFILE_URL2 = MOBILE_FACEBOOK+FID_QUERY.strip('/')
BASIC_Q = ["groups", "pages-liked", "friends", "followers", "stories-liked", "photos-liked", "videos-liked",
           "stories-commented", "photos-commented", "videos-commented", "apps-used"]
COMMANDS_Q = ["--posts", "--about", "--exist", "--profile_photos", "--screenshots",
              "--reverse_image_google", "--reverse_image_tineye"]
INTERSECT = "/intersect"

MUTUAL = "browse/mutual_friends/"
LINK_REF = '?ref=br_rs'
LINK_FREF = "fref=pb"
# ****************************************Search queries on a profile*******************************************
GROUPS_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[0]
PAGES_LIKED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[1]
FRIENDS_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[2]
FOLLOWERS_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[3]
STORIES_LIKED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[4]
PHOTOS_LIKED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[5]
VIDEOS_LIKED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[6]
STORIES_COMMENTED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[7]
PHOTOS_COMMENTED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[8]
VIDEOS_COMMENTED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[9]
APPS_USED_Q = FACEBOOK_SEARCH+FID_QUERY+BASIC_Q[10]
SCREENSHOTS_Q = BASE_PROFILE_URL+"--screenshots"
POSTS_Q = BASE_PROFILE_URL2+'--posts'
ABOUT_Q = BASE_PROFILE_URL2+'--about'
EXIST_Q = BASE_PROFILE_URL2+'--exist'
PROFILE_PHOTOS_Q = FACEBOOK+FID_QUERY.strip('/')+'--profile_photos'
SEARCH_IMAGE_GOOGLE = FACEBOOK+FID_QUERY.strip('/')+'--reverse_image_google'
SEARCH_IMAGE_TINEYE = FID_QUERY.strip('/')+"--reverse_image_tineye"
BUILD_PROFILE = '--build_profile'

Q_FOR_SCREENSHOTS = [GROUPS_Q, PAGES_LIKED_Q, PHOTOS_COMMENTED_Q, PHOTOS_LIKED_Q, STORIES_COMMENTED_Q]
# ****************************************Search queries to compare between profiles****************************
COMMON_GROUPS_Q = GROUPS_Q+FID_QUERY+BASIC_Q[0]+INTERSECT
COMMON_PAGES_LIKED_Q = PAGES_LIKED_Q+FID_QUERY+BASIC_Q[1]+INTERSECT
COMMON_FRIENDS_Q = FACEBOOK+MUTUAL+"?uid="+FID_QUERY.strip('/')+"&node="+FID_QUERY.strip("/")
COMMON_FOLLOWERS_Q = FOLLOWERS_Q+FID_QUERY+BASIC_Q[3]+INTERSECT
COMMON_STORIES_LIKED_Q = STORIES_LIKED_Q+FID_QUERY+BASIC_Q[4]+INTERSECT
COMMON_PHOTOS_LIKED_Q = PHOTOS_LIKED_Q+FID_QUERY+BASIC_Q[5]+INTERSECT
COMMON_VIDEOS_LIKED_Q = VIDEOS_LIKED_Q+FID_QUERY+BASIC_Q[6]+INTERSECT
COMMON_STORIES_COMMENTED_Q = STORIES_COMMENTED_Q+FID_QUERY+BASIC_Q[7]+INTERSECT
COMMON_PHOTOS_COMMENTED_Q = PHOTOS_COMMENTED_Q+FID_QUERY+BASIC_Q[8]+INTERSECT
COMMON_VIDEOS_COMMENTED_Q = VIDEOS_COMMENTED_Q+FID_QUERY+BASIC_Q[9]+INTERSECT
COMMON_APPS_USED_Q = APPS_USED_Q+FID_QUERY+BASIC_Q[10]+INTERSECT

# ************************************XPATH strings to find facebook elements***********************************
HOME_XPATH = r"//*[text()[contains(.,'Home')]]"
TL_XPATH = r"//*[text()[contains(.,'Timeline')]]"
ABOUT_XPATH = r"//*[text()[contains(.,'About')]]"
PHOTOS_XPATH = r"//*[text()[contains(.,'Photos')]]"
ALBUMS_XPATH = r"//*[text()[contains(.,'Albums')]]"
PROFILE_PICTURES_XPATH = r"//a[text()[contains(.,'Profile Pictures')]]"
SHOW_MORE_XPATH = r"//*[text()[contains(.,'Show more')]]"
SEE_MORE_XPATH_LIST = [r"//*[text()[contains(.,'Show more')]]", r"//*[text()[contains(.,'Show More')]]",
                       r"//*[text()[contains(.,'show more')]]", r"//*[text()[contains(.,'See more')]]",
                       r"//*[text()[contains(.,'See More')]]", r"//*[text()[contains(.,'see more')]]",
                       r"//*[text()[contains(.,'See More Stories')]]"]
BLOCK_PROF_XPATH = r"//*[text()[contains(.,'Block this person')]]"
# ARTICLE_XPATH = r"//div[@role = 'article']]"
INTEL_TECH_MENU = r"//a[text()[contains(.,'Tools')]]"
INTEL_TECH_FB = r"//a[text()[contains(.,'FACEBOOK')]]"
"""
<a href="osint/menu.facebook.html" target="innerframe">&nbsp;&nbsp;&nbsp;FACEBOOK</a>
"""
# ************************************JavaScript commands for WebDriver*****************************************
GO_BACK = "window.history.go(-1)"
RET_SCROLL_HEIGHT = "return document.body.scrollHeight"
SCROLL_TO = "window.scrollTo(0, document.body.scrollHeight);"

# ****************************************Folder paths for saving files*******************************************
DESKTOP_PATH = os.path.join(os.environ["HOMEPATH"], "DESKTOP")
SAVE_PATH = os.path.join(os.environ["HOMEPATH"], "DESKTOP", "CSV")
PATH_REPORTS = os.path.join(DESKTOP_PATH, 'profile_reports')
PATH_GROUPS = os.path.join(SAVE_PATH, BASIC_Q[0])
PATH_PAGES = os.path.join(SAVE_PATH, BASIC_Q[1])
PATH_FRIENDS = os.path.join(SAVE_PATH, BASIC_Q[2])
PATH_FOLLOWERS = os.path.join(SAVE_PATH, BASIC_Q[3])
PATH_STORIES_LIKED = os.path.join(SAVE_PATH, BASIC_Q[4])
PATH_PHOTOS_LIKED = os.path.join(SAVE_PATH, BASIC_Q[5])
PATH_VIDEOS_LIKED = os.path.join(SAVE_PATH, BASIC_Q[6])
PATH_STORIES_COMMENTED = os.path.join(SAVE_PATH, BASIC_Q[7])
PATH_PHOTOS_COMMENTED = os.path.join(SAVE_PATH, BASIC_Q[8])
PATH_VIDEOS_COMMENTED = os.path.join(SAVE_PATH, BASIC_Q[9])
PATH_APPS = os.path.join(SAVE_PATH, BASIC_Q[10])
PATH_POSTS = os.path.join(SAVE_PATH, 'posts')
PATH_PHOTOS = os.path.join(DESKTOP_PATH, 'profile_pics')
PATH_SCREENSHOTS = os.path.join(DESKTOP_PATH, 'screenshots')
PATH_ABOUT = os.path.join(SAVE_PATH, 'about')
PATH_EXIST = os.path.join(SAVE_PATH, 'exist_on_facebook')

ALL_PATHS = [PATH_GROUPS, PATH_PAGES, PATH_FRIENDS, PATH_FOLLOWERS, PATH_STORIES_LIKED, PATH_PHOTOS_LIKED,
             PATH_VIDEOS_LIKED, PATH_STORIES_COMMENTED, PATH_PHOTOS_COMMENTED, PATH_VIDEOS_COMMENTED,
             PATH_APPS, PATH_POSTS, PATH_PHOTOS, PATH_SCREENSHOTS, PATH_ABOUT, PATH_EXIST]
# ************************************Columns for Pandas DataFrame************************************************
GROUPS_COL = [r"UID", r"Profile Name", r"Group Name", r"Group ID", r"Members", r"Group Type", r"Time Stamp"]
PAGES_LIKED_COL = ["UID", r"Profile Name", r"Page Name", r"Page ID", r"Likes", r"Ranking",
                   r"Page Place", r"Page Category", r"Time Stamp"]
FRIENDS_COL = [r"UID", r"Profile Name", r"Friend Name", r"Friend ID", r"Work", r"Education", r"Current City",
               r"Hometown", r"Age", r"Gender", r"Interest", r"Relationship Status", r"Time Stamp"]
FOLLOWERS_COL = [r"UID", r"Profile Name", r"Follower Name", r"Follower ID", r"Work", r"Education", r"Current City",
                 r"Hometown", r"Age", r"Gender", r"Interest", r"Relationship Status", r"Time Stamp"]
STORIES_LIKED_COL = [r"UID", r"Profile Name", r"Post Title", r"Post Text",
                     r"Upload Time", r"Location", r"Likes", r"Comments", r"Shares", r"Time Stamp"]
PHOTOS_LIKED_COL = [r"UID", r"Profile Name", r"Photo URL", r"Photo Src", r"Uploader Name",
                    r"Uploader ID", r"Likes", r"Comments", r"Time Stamp"]
VIDEOS_LIKED_COL = [r"UID", r"Profile Name", r"Video Title", r"Video Link", r"Uploader Name",
                    r"Uploader ID", r"Upload Time", r"Views", r"Duration", r"Time Stamp"]
STORIES_COMMENTED_COL = [r"UID", r"Profile Name", r"Post Title", r"Post Text",
                         r"Upload Time", r"Location", r"Likes", r"Comments", r"Shares", r"Time Stamp"]
PHOTOS_COMMENTED_COL = [r"UID", r"Profile Name", r"Photo URL", r"Photo Src", r"Uploader Name",
                        r"Uploader ID", r"Likes", r"Comments", r"Time Stamp"]
VIDEOS_COMMENTED_COL = [r"UID", r"Profile Name", r"Video Title", r"Video Link", r"Uploader Name",
                        r"Uploader ID", r"Upload Time", r"Views", r"Duration", r"Time Stamp"]
APPS_USED_COL = [r"UID", r"Profile Name", r"App Name", r"App ID", r"App Rating", r"Category",
                 r"Time Stamp"]

POSTS_COL = [r"UID", r"Profile Name", r"Post Title", r"Post Text", r"Upload Time",
             r"CheckIn", r"Hashtags", r"Links", r"Tagged People", r"Likes",
             r"Comments", r"Shares", r"Photo Src", r"Post Type", r"Time Stamp"]

# TODO add Professional Skills
ABOUT_COL = [r"UID", r"User Name", r"Profile Name", r"Profile Image Link", r"Profile Image Src",
             r"Has Phone?", r"Intro Description", r"Education1", r"Education2", r"Education3",
             r"Education4", r"Education5", r"Education6", r"Work1", r"Work2", r"Work3", r"Work4",
             r"Work5", r"Work6", r"Current City", r"Hometown", "Phone Number", r"Email",
             r"Facebook", r"Instagram", r"Twitter", r"Snapchat", r"Youtube", r"LinkedIn", r"Skype",
             r"Website1", r"Website2", r"Website3", r"Contact Info1",
             r"Contact Info2", r"Contact Info3", r"Birthday", r"Gender", r"Interested In",
             r"Languages", r"Religious Views", r"Political Views", r"Basic Info1", r"Basic Info2",
             r"Basic Info3", "Nickname1", r"Nickname2", r"Maiden Name", r"Alternative Name",
             r"Married Name", r"Father's Name", r"Birth Name", r"Former Name", r"Name With Title",
             r"Other Name1", r"Other Name2", r"Other Name3", r"Relationship Status",
             r"Family Member1", r"Family Member2", r"Family Member3", r"Family Member4",
             r"Family Member5", r"Family Member6", r"Family Member7", r"Family Member8",
             r"Family Member9", r"Family Member10", r"Bio", r"Life Event1", r"Life Event2",
             r"Life Event3", r"Life Event4", r"Life Event5", r"Life Event6",
             r"Life Event7", r"Life Event8", r"Life Event9", r"Life Event10",
             r"Favourite Quotes", r"Time Stamp"]

EXIST_COL = [r"UID", r"Profile Name", r"Exists On Facebook", r"Time Stamp"]
PROFILE_PHOTOS_COL = [r"UID", r"Profile Name", r"Stolen Photos?", r"Stolen Image URL", r"Time Stamp"]
COMMON_GROUPS_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2",
                     r"Group Name", r"Group ID", r"Members", r"Group Type", r"Time Stamp"]
COMMON_PAGES_LIKED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Page Name",
                          r"Page ID", r"Likes", r"Ranking", r"Page Place", r"Page Category", r"Time Stamp"]
"""
COMMON_FRIENDS_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Friend Name",
                      r"Friend ID",  r"Work", r"Education", r"Current City", r"Hometown",
                      r"Age", r"Gender", r"Interest", r"Relationship Status", r"Time Stamp"]
"""
MUTUAL_FRIENDS_COL = [r"UID", r"UID2", r"Friend Name", r"Friend ID", r"Time Stamp"]
COMMON_FOLLOWERS_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Follower Name",
                        r"Follower ID", r"Work", r"Education", r"Current City", r"Hometown",
                        r"Age", r"Gender", r"Interest", r"Relationship Status", r"Time Stamp"]
COMMON_STORIES_LIKED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Post Title",
                            r"Post Text", r"Upload Time", r"Location", r"Likes", r"Comments",
                            r"Shares", r"Time Stamp"]
COMMON_PHOTOS_LIKED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Photo URL",
                           r"Photo src", r"Uploader Name", r"Uploader ID", r"Likes",
                           r"Comments", r"Time Stamp"]
COMMON_VIDEOS_LIKED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Video Title",
                           r"Video Link", r"Uploader Name", r"Uploader ID", r"Upload Time",
                           r"Views", r"Duration", r"Time Stamp"]
COMMON_STORIES_COMMENTED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Post Title",
                                r"Post Text", r"Upload Time", r"Location", r"Likes", r"Comments",
                                r"Shares", r"Time Stamp"]
COMMON_PHOTOS_COMMENTED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Photo URL",
                               r"Photo src", r"Uploader Name", r"Uploader ID", r"Likes",
                               r"Comments", r"Time Stamp"]
COMMON_VIDEOS_COMMENTED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"Video Title",
                               r"Video Link", r"Uploader Name", r"Uploader ID", r"Upload Time",
                               r"Views", r"Duration", r"Time Stamp"]
COMMON_APPS_USED_COL = [r"UID", r"Profile Name", r"UID2", r"Profile Name2", r"App Name",
                        r"App ID", r"App Rating", r"Category", r"Time Stamp"]

RELATIONSHIP_OPTS = [r"Single", r"Married", r"Divorced", r"It's complicated", r"In a relationship", r"Engaged",
                     r"In a civil union", r"In an open relationship", r"Separated", r"Widowed", r"In a domestic relationship"]


SECURITY_KW = r'Security|Another pattern'


def columns_from_cond(x):
    # returns list of columns for pandas DataFrame or csv, by given command/query
    return {
        COMMANDS_Q[0]: POSTS_COL, COMMANDS_Q[1]: ABOUT_COL,
        COMMANDS_Q[2]: EXIST_COL, COMMANDS_Q[3]: PROFILE_PHOTOS_COL,
        BASIC_Q[0]: GROUPS_COL, BASIC_Q[1]: PAGES_LIKED_COL, BASIC_Q[2]: FRIENDS_COL,
        BASIC_Q[3]: FOLLOWERS_COL, BASIC_Q[4]: STORIES_LIKED_COL, BASIC_Q[5]: PHOTOS_LIKED_COL,
        BASIC_Q[6]: VIDEOS_LIKED_COL, BASIC_Q[7]: STORIES_COMMENTED_COL, BASIC_Q[8]: PHOTOS_COMMENTED_COL,
        BASIC_Q[9]: VIDEOS_COMMENTED_COL, BASIC_Q[10]: APPS_USED_COL, BASIC_Q[0]+INTERSECT: COMMON_GROUPS_COL,
        BASIC_Q[1]+INTERSECT: COMMON_PAGES_LIKED_COL, BASIC_Q[2]+INTERSECT: None, MUTUAL: MUTUAL_FRIENDS_COL,
        BASIC_Q[3]+INTERSECT: COMMON_FOLLOWERS_COL, BASIC_Q[4]+INTERSECT: COMMON_STORIES_LIKED_COL,
        BASIC_Q[5]+INTERSECT: COMMON_PHOTOS_LIKED_COL, BASIC_Q[6]+INTERSECT: COMMON_VIDEOS_LIKED_COL,
        BASIC_Q[7]+INTERSECT: COMMON_STORIES_COMMENTED_COL, BASIC_Q[8]+INTERSECT: COMMON_PHOTOS_COMMENTED_COL,
        BASIC_Q[9]+INTERSECT: COMMON_VIDEOS_COMMENTED_COL, BASIC_Q[10]+INTERSECT: COMMON_APPS_USED_COL,
    }[x]


def ret_cols(target_url):
    # returns list of columns for pandas DataFrame or csv, by url (string)
    columns = []
    tmp_qs_list = [MUTUAL]+BASIC_Q+COMMANDS_Q
    for index in tmp_qs_list:
        if index in target_url:
            if INTERSECT in target_url:
                columns = columns_from_cond(index+INTERSECT)  # get required columns, by query from url
            else:
                columns = columns_from_cond(index)  # get required columns, by query from url
            break
    return columns


def ret_save_path(target_url):
    # choose path to directory for saving data, by target url
    tmp_qs_list = BASIC_Q+COMMANDS_Q
    for index in tmp_qs_list:
        if index in target_url:
            return path_by_cond(index), index.replace('--', '')
    return SAVE_PATH, "CSV"


def path_by_cond(x):
    # choose path to directory for saving data, by command/query
    return {
        COMMANDS_Q[0]: PATH_POSTS, COMMANDS_Q[1]: PATH_ABOUT, COMMANDS_Q[2]: PATH_EXIST,
        COMMANDS_Q[3]: PATH_PHOTOS, BASIC_Q[0]: PATH_GROUPS, BASIC_Q[1]: PATH_PAGES,
        BASIC_Q[2]: PATH_FRIENDS, BASIC_Q[3]: PATH_FOLLOWERS, BASIC_Q[4]: PATH_STORIES_LIKED,
        BASIC_Q[5]: PATH_PHOTOS_LIKED, BASIC_Q[6]: PATH_VIDEOS_LIKED, BASIC_Q[7]: PATH_STORIES_COMMENTED,
        BASIC_Q[8]: PATH_PHOTOS_COMMENTED, BASIC_Q[9]: PATH_VIDEOS_COMMENTED, BASIC_Q[10]: PATH_APPS,
    }[x]


def set_raw_data(columns):
    # set dictionary with a list of columns - as dictionary's keys
    raw_data = dict.fromkeys(columns)
    for i, j in raw_data.items():
        raw_data[i] = []
    return raw_data


def remove_temp_file():
    # remove the temp file from desktop
    try:
        os.remove(os.path.join(DESKTOP_PATH, "tmp_file.txt"))
    except FileNotFoundError:
        pass
    except NotImplementedError:
        pass


def create_dir(path):
    # create new directory if not existed before
    if not os.path.exists(path):
        os.makedirs(path)


def create_dirs_for_screenshots(profile_name):
    # create dirs by given paths (include profile name)
    path_to_create = os.path.join(PATH_SCREENSHOTS, profile_name)
    create_dir(path_to_create)
    create_dir(os.path.join(path_to_create, profile_name+'#groups'))
    create_dir(os.path.join(path_to_create, profile_name+'#groups'))
    create_dir(os.path.join(path_to_create, profile_name+'#pages-liked'))
    create_dir(os.path.join(path_to_create, profile_name+'#photos-commented'))
    create_dir(os.path.join(path_to_create, profile_name+'#photos-liked'))
    create_dir(os.path.join(path_to_create, profile_name+'#stories-commented'))


def ret_current_time():
    # returns current date and time (string)
    return datetime.strftime(datetime.today(), "%d_%m_%y#%H-%M")


def ret_time_stamp():
    # returns current date and time (string) - in format for time stamp
    # 'weekday month day hour:minute:second year', for example: Wed May 17 20:09:43 2015
    return datetime.today().ctime()


def ret_current_year():
    # returns current year (int)
    return datetime.now().year


def text_from_file(file_name):
    # open file by given path
    res = []
    if os.path.exists(file_name) and os.path.isfile(file_name):
        with codecs.open(file_name, 'r', encoding='utf-8') as this_file:
            for line in this_file.readlines():
                res.append(line.replace('\n', '').replace('\r', ''))
        this_file.close()
    return res


def enable_js_preference():
    # fixes problem that enforces javascript to be disabled on browser as default
    f = open(os.path.join(PREFERENCES_PATH, 'Preferences'), "r+")
    d = f.readlines()
    f.seek(0)
    for i in d:
        if r',"managed_default_content_settings":{"javascript":2}' in i:
            f.write(i.replace(r',"managed_default_content_settings":{"javascript":2}', ''))
        else:
            f.write(i)
    f.truncate()
    f.close()
