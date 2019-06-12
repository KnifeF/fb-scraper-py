"""
The program gets facebook profiles (User IDs) as an input (through Tkinter GUI),
navigates to related facebook web pages and data for scraping, and then generates reports
or finds some basic insights within the data. the process is based on tools like selenium webdriver, pyautogui,
beautifulsoup, re - to scrape the web & parse some html. the data is stored in various ways (CSV, docx, txt).
This is an old&basic code (not so pretty.. with some possibly errors..) that I have written for educational purposes.
*You may see more details on the README.md file.

## Disclaimer:
The scripts / tools are for educational purposes only,
and they might violate some websites (including social media/search engines) TOS.
Use at your own risk.
"""

import glob
from program_gui import GuiMenu
from auto_img_on_web import *
from fb_results_parser import facebook_results_parser
from fb_about_parser import parse_about_target
from fb_timeline_parser import parse_target_posts
from build_fb_profile import FbProfile
from selenium import webdriver
from selenium.common.exceptions import *
from random import randint
from time import sleep


# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


# *****************************Functions of the crawler*********************************************
class FacebookCrawler:

    def __init__(self, targets, mobile_targets, ids_to_check_on_tineye):
        # Build FacebookCrawler obj
        self.targets = targets  # facebook urls to crawl
        self.mobile_targets = mobile_targets  # facebook urls to crawl in mobile version (when js disabled)
        # facebook uids to search their photos (from .jpg files in profile's dir) in TinEye
        self.ids_to_check_on_tineye = ids_to_check_on_tineye
        self.driver = None
        self.js_enabled = True
        if self.mobile_targets:
            self.js_enabled = False
        self.set_chrome_driver()  # sets required options and arguments in 'webdriver.Chrome'

    def set_chrome_driver(self, incognito=None):
        # Set chromedriver to the desirable mode (with options and arguments)
        options = webdriver.ChromeOptions()
        if incognito:
            options.add_argument("--incognito")  # incognito mode in chrome without using 'User Data'
        else:
            options.add_argument(ARGUMENTS)  # set dir with chrome 'User Data' (include exist cookies)
        if not self.js_enabled:
            options.add_experimental_option("prefs", PREFERENCES)  # option that disables JavaScript in chrome
        options.add_argument(WITHOUT_EXTENSIONS)  # disable extensions in chrome
        # creating object (webdriver.Chrome)
        chrome_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=options)
        chrome_driver.maximize_window()  # maximize window's size of the browser ('webdriver')
        self.driver = chrome_driver

    def switch_window(self):
        # switch between windows of the WebDriver (useful when working with two opened tabs)
        if self.driver:
            if len(self.driver.window_handles) == 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
            elif len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[1])
            sleep(3)

    def reopen_driver(self, incognito=None, disable_js=None):
        # open new WebDriver if not opened yet
        if incognito:
            self.driver.delete_all_cookies()
        if disable_js:
            self.js_enabled = False
        else:
            self.js_enabled = True
        self.destroy_driver()
        sleep(randint(30, 4*60))
        self.set_chrome_driver(incognito=incognito)  # sets required options and arguments in 'webdriver.Chrome'

    def destroy_driver(self):
        # close the drivers and set the WebDriver value to 'None'
        if self.driver:
            self.driver.close()  # close WebDriver
            self.driver = None  # change value to None
        enable_js_preference()  # fix javascript to be enabled on chrome browser

    def scroll_by(self, height_to_scroll=400):
        # scroll page by height (400 as default)
        # height_to_scroll = 400
        # scrolling page
        sleep(randint(2, 3))
        self.driver.execute_script("window.scrollBy(0, %d);" % height_to_scroll)
        # Wait to load page
        sleep(randint(2, 3))

    def scroll_down_page(self):
        # scrolling page to get more data from target url
        sleep(randint(3, 9))
        current_source = self.driver.page_source
        if not("We couldn't find anything for" in current_source
               or "Looking for people or posts?" in current_source
               or "This page isn't available" in current_source):
            # Get scroll height
            last_height = self.driver.execute_script(RET_SCROLL_HEIGHT)
            count = 0
            while True:
                sleep(randint(1, 4))
                # Scroll down to bottom
                self.driver.execute_script(SCROLL_TO)
                # Wait to load page
                sleep(randint(1, 6))
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script(RET_SCROLL_HEIGHT)
                sleep(randint(1, 3))
                if new_height == last_height:
                    count += 1
                    sleep(2)
                    current_source = self.driver.page_source
                    if (count >= 10) or ("End of Results" in current_source) or \
                            ("We couldn't find anything for" in current_source) \
                            or ("Bing Privacy Policy" in current_source):
                        sleep(randint(1, 2))
                        break
                else:
                    count = 0
                last_height = new_height

    def find_see_more_button(self):
        # find required button by xpath
        for tmp_xpath in SEE_MORE_XPATH_LIST:
            try:
                sleep(randint(2, 4))
                see_more_elem = self.driver.find_elements_by_xpath(tmp_xpath)
                if see_more_elem:
                    print(tmp_xpath)
                    return see_more_elem
            except WebDriverException:
                print("WebDriverException")
                pass
        return None

    def see_more_loop(self, all_htm):
        # Loop that clicks on 'show more' to get more data from timeline (fb mobile version)
        see_more_elem = self.find_see_more_button()
        count = 0
        while see_more_elem and ('timeline' in self.driver.current_url or 'profile' in self.driver.current_url
                                 or 'tmln' in self.driver.current_url):
            try:
                sleep(randint(3, 12))
                see_more_elem[0].click()  # click button
                count += 1
                sleep(randint(2, 4))
                all_htm.append(self.driver.page_source)  # append current page source to list
                sleep(randint(1, 3))
                # find required button by xpath
                # see_more_elem = self.driver.find_elements_by_xpath(SHOW_MORE_XPATH)
                see_more_elem = self.find_see_more_button()
                if count > 50:
                    break
            except WebDriverException:
                print("WebDriverException")
                pass
        return all_htm

    def see_more_years(self, all_htm):
        # Loop of clicks on a range of years to get more data from timeline (fb mobile version)
        # years_to_scroll = range(datetime.now().year, 1960, -1)
        years_to_scroll = range(ret_current_year(), 2016, -1)  # list with years range to search for
        for tmp_year in years_to_scroll:
            try:
                y_path = r"//a[text()[contains(.,'%s')]]" % tmp_year  # insert year from list to xpath
                year_buttons = self.driver.find_elements_by_xpath(y_path)  # find required element by xpath
                if len(year_buttons) > 0:
                    sleep(randint(3, 12))
                    self.driver.find_elements_by_xpath(y_path)[0].click()  # click on element
                    sleep(randint(2, 4))
                    all_htm.append(self.driver.page_source)  # append current page source to list
                    sleep(randint(2, 4))
                    # Loop to get more data from posts in given year
                    all_htm = self.see_more_loop(all_htm)
                    sleep(randint(1, 3))
            except WebDriverException:
                print("WebDriverException")
                pass
        return all_htm

    def profile_found(self, facebook_uid):
        # return False if the profile has not been found, else True
        self.driver.get(FACEBOOK+"profile.php?id="+facebook_uid)  # get facebook profile page
        sleep(randint(3, 5))  # wait to load page
        current_source = self.driver.page_source  # current page source
        if ("This Page Isn't available" in current_source) or ("page may have been removed" in current_source) or \
                ("The link" in current_source and "broken" in current_source):
            # return if profile not found
            return False
        return True

    def rand_navigation_home(self):
        # randomly navigates to facebook home page
        to_home = randint(1, 4)
        sleep(randint(5, 20))
        if to_home == 3:
            # get facebook url of main page by clicking 'Home' button
            self.navigate_by_xpath('home')

    def crawl_all_targets(self):
        # Crawl all targets and extract required data (from facebook, google and tineye)
        if self.driver:
            if self.mobile_targets:
                # crawl facebook targets with mobile version (js disabled)
                self.crawl_targets_on_mobile()
            if self.targets:
                # crawl facebook targets with web version (js enabled)
                self.crawl_targets_on_web()
            if self.ids_to_check_on_tineye:
                # upload & search profiles' pictures, to find matches on Tineye (image search engine)
                self.target_pics_on_tineye()
        print("finish crawling targets...")
        self.destroy_driver()

    def crawl_targets_on_mobile(self):
        # Crawl facebook targets and extract data - facebook mobile version
        sleep(2)
        self.driver.get(MOBILE_FACEBOOK)  # get facebook url of main page on mobile version
        for target_url in self.mobile_targets:
            sleep(randint(10, 2*60))
            print("start crawling %s --> %s" % (target_url, ret_time_stamp()))
            if '--' in target_url:
                fb_url = target_url.split('--')[0]  # url without the given command in original string
                command_for_crawler = target_url.split('--')[1]  # given command (includes what to scrape)
                self.driver.get(fb_url+"?_rdr")  # get specific facebook url to crawl
                sleep(randint(3, 8))
                self.scrape_by_command(fb_url, command_for_crawler)  # choose what to scrape from profile by command
            self.rand_navigation_home()  # go randomly to facebook home page
            print("end crawling %s --> %s" % (target_url, ret_time_stamp()))

    def crawl_targets_on_web(self):
        # Crawl facebook targets and extract data - facebook web version
        if self.mobile_targets:
            self.reopen_driver()
        self.driver.get(FACEBOOK)  # get facebook url of main page
        sleep(randint(10, 30))

        for target_url in self.targets:
            if len(self.targets) > 10:
                sleep(randint(10, 2*60))
            else:
                sleep(randint(10, 30))
            if randint(0, 5) == 1:
                move_randomly_on_screen(to_top=True, scroll_down=True)  # auto move of mouse, or a press on keys
            if "--" in target_url:
                fb_url = target_url.split('--')[0]  # url without the given command in original string
                command_for_crawler = target_url.split('--')[1]  # given command (includes what to scrape)
                self.scrape_by_command(fb_url, command_for_crawler)  # choose what to scrape from profile by command
            else:
                self.driver.get(target_url)  # get specific facebook url to crawl
                self.scroll_down_page()  # scroll facebook page to view more results on the html
                sleep(randint(2, 5))
                facebook_results_parser(target_url, self.driver.page_source)  # parse data from facebook page
            self.rand_navigation_home()  # go randomly to facebook home page
            print("end crawling %s --> %s" % (target_url, ret_time_stamp()))

    def scrape_target_posts(self, target_url):
        # scrape posts from profile's 'Timeline' & parse results to csv
        all_htm = []
        self.navigate_by_xpath('timeline')  # make sure the profile has navigated to 'Timeline' section
        # find elements by given id (indicates that timeline section appears)
        is_tl = None
        try:
            is_tl = (self.driver.find_elements_by_id("timelineBody"))
        except WebDriverException:
            print("WebDriverException")
            pass

        if is_tl:
            all_htm.append(self.driver.page_source)  # append current page source of WebDriver to list
            sleep(2)
            # loops that clicks on buttons, to view more posts, and append page sources to list
            all_htm = self.see_more_loop(all_htm)  # loop to view more posts by 'See more' button
            all_htm = self.see_more_years(all_htm)  # loop to view more posts by years in timeline
            sleep(randint(2, 5))
            # parse timeline posts of target and store in csv
            parse_target_posts(target_url, all_htm)

    def scrape_about_target(self, target_url):
        # scrape details about a profile from 'About' section & parse results to csv
        self.navigate_by_xpath('about')  # make sure the profile has navigated to 'About' section
        try:
            sleep(randint(5, 10))
            current_source = self.driver.page_source  # current source of page
            current_url = self.driver.current_url  # current url of page
            if ("This Page Isn't available" in current_source) or ("page may have been removed" in current_source) or \
                    ("The link" in current_source and "broken" in current_source):
                return
            # indicate navigation to 'About' section
            if self.driver.find_element_by_id('root') or '/about' in current_url:
                parse_about_target(target_url, current_url, current_source)  # parse data about target and store in csv
        except WebDriverException:
            print("WebDriverException")
            pass
        return False

    def is_target_on_facebook(self, facebook_uid):
        # check if the required facebook profile appears on facebook
        create_dir(PATH_EXIST)  # create dirs with given path when necessary
        current_time = ret_current_time()  # current time
        tmp_file_name = os.path.join(PATH_EXIST, 'profile_exist_status.csv')  # file name to save
        prof_exist = "No"
        prof_name = "X"

        self.navigate_by_xpath('timeline')  # make sure the profile has navigated to 'Timeline' section

        prof_cover_elem = self.driver.find_elements_by_id("m-timeline-cover-section")  # timeline section appears
        prof_tl_elem = self.driver.find_elements_by_id('timelineBody')  # timeline section appears
        # search for elements and buttons to indicate that the profile exist on facebook
        if (prof_tl_elem or prof_cover_elem) \
                or (self.driver.find_elements_by_id(BLOCK_PROF_XPATH)
                    and (self.driver.find_elements_by_xpath(TL_XPATH)
                         or self.driver.find_elements_by_xpath(ABOUT_XPATH))):
            prof_exist = "Yes"
            # profile name is usually the title of browser (when in profile page)
            prof_name = self.driver.title

        # take a screenshot to indicate that the profile is found
        take_a_screenshot(os.path.join(PATH_EXIST, facebook_uid+"#"+prof_exist+"#"+current_time+".png"))
        # saves data to csv
        with codecs.open(tmp_file_name, 'a', encoding='utf-8-sig') as out_f:
            tmp_writer = csv.writer(out_f, dialect='excel', delimiter=',', quotechar='"',
                                    skipinitialspace=True)
            if os.stat(tmp_file_name).st_size == 0:
                tmp_writer.writerow(EXIST_COL)
            tmp_writer.writerow([facebook_uid, prof_name, prof_exist, current_time])
        out_f.close()

    def screenshots_of_target(self, facebook_uid):
        # take screenshots of profile timeline, photos and required activities on facebook
        if self.profile_found(facebook_uid):
            profile_name = self.driver.title  # profile name
            create_dirs_for_screenshots(profile_name)  # create dirs for screenshots of profile
            # queries (for url) to take screenshot from

            queries_lst = ['timeline', 'profile_pictures', 'groups', 'pages-liked',
                           'photos-commented', 'photos-liked', 'stories-commented']
            for index in range(len(queries_lst)):
                query = queries_lst[index]
                if query:
                    sleep(randint(10, 40))
                    count_limit = 3
                    if ('timeline' not in query) and ("profile_pictures" not in query):
                        # get facebook page by query
                        self.driver.get(FACEBOOK_SEARCH+"/"+facebook_uid+"/"+query)
                        sleep(randint(3, 9))
                        count_limit = 50
                    elif "profile_pictures" in query:
                        count_limit = 0
                        # screenshots of target's profile photos
                        self.crawl_target_photos(facebook_uid, prof_name=profile_name, screen_image=True)

                    if not("We couldn't find anything for" in self.driver.page_source
                           or "Looking for people or posts?" in self.driver.page_source):  # found results
                        count = 0
                        while (count < count_limit) and ("End of Results" not in self.driver.page_source):
                            screenshot_by_query(profile_name, query, count+1)  # take a screenshot by query
                            self.scroll_by()  # scrolling down page (in web page)
                            count += 1
                        if ('timeline' not in query) and ("profile_pictures" not in query):
                            screenshot_by_query(profile_name, query, count+1)  # take a screenshot by query

    def crawl_target_photos(self, facebook_uid, prof_name=None, save_image=None,
                            search_image=None, screen_image=None):
        # crawl target's profile photos - save to jpg files/search in google/take screenshots
        if self.profile_found(facebook_uid):
            sleep(randint(3, 15))
            if not prof_name:
                prof_name = self.driver.title  # profile name from WebDriver current title

            # find profile pics elements ('profilePic' is a partial string in <a> tag class, of a profile pic)
            photo_elems = self.driver.find_elements_by_css_selector("a[class*='profilePic']")
            if len(photo_elems) > 0:
                try:
                    # click on current profile picture (last updated pic)
                    self.driver.find_elements_by_css_selector("a[class*='profilePic']")[0].click()
                except WebDriverException:
                    print('WebDriverException')
                    pass

                sleep(randint(3, 9))
                current_url = self.driver.current_url  # current url of the WebDriver

                # set paths and dirs to save the profile pictures
                path_for_pics = os.path.join(PATH_PHOTOS, facebook_uid)  # path for profile's pictures
                f_name_image_search = os.path.join(path_for_pics, facebook_uid+"#profile_pics_on_web.csv")
                create_dir(path_for_pics)  # create dirs from given path

                photos_urls = []  # list to contain all photo urls
                count_photos = 0  # count loop repeats to limit photo downloads

                # loop till limit of photos to download, or when repeat on same url (known url)
                while (current_url not in photos_urls) and (count_photos < 15):
                    try:
                        sleep(randint(8, 40))
                        current_source = self.driver.page_source  # current page source

                        find_esc_option = re.findall('Press Esc to close', current_source)
                        print(find_esc_option)
                        # check if url related to photo, or if a photo opened (after the click)
                        if 'photo.php?fbid' in current_url or find_esc_option:
                            photos_urls.append(current_url)  # append url to the list of photo urls
                            sleep(2)
                            # try to find if people are found in photo
                            people_in_pic = identify_people_in_profile_picture(current_source, prof_name)
                            is_saving_position = False
                            if people_in_pic or find_esc_option:  # people have been found in photo
                                # find cursor position that enables to save the photo/search it on google
                                is_saving_position, pos_x, pos_y = \
                                    find_img_saving_pos(save_image, search_image, screen_image)

                            # attempts to save profile pic/search it on Google/take screenshots
                            if is_saving_position and (pos_x and pos_y):
                                sleep(randint(2, 5))
                                pyautogui.moveTo(pos_x,  pos_y, 1)  # moving mouse to given pixels on screen
                                if save_image:  # 'save image' option
                                    save_profile_pic(path_for_pics, count_photos)  # download image from facebook
                                elif search_image:  # 'Search Google for image' option
                                    self.search_and_scrape_pic(facebook_uid, current_url, f_name_image_search,
                                                               path_for_pics, count_photos)
                                elif screen_image:  # 'screenshot of image' option
                                    if prof_name:
                                        screenshot_by_query(prof_name, 'profile_pictures', count_photos+1)
                                    elif facebook_uid:
                                        screenshot_by_query(facebook_uid, 'profile_pictures', count_photos+1)
                            elif count_photos >= 0:
                                count_photos -= 1
                            count_photos += 1
                            sleep(randint(2, 5))
                            move_to_next_profile_pic()  # move to next pic by pressing 'right'
                            sleep(3)  # wait to load new url (after moving to next pic)
                            current_url = self.driver.current_url  # current url of the WebDriver
                            sleep(1)
                        else:
                            break
                    except WebDriverException:
                        print("WebDriverException")
                        pass
                sleep(randint(3, 9))
                pyautogui.press("esc")  # press 'Esc', to close the album and return to profile's page

    def search_and_scrape_pic(self, facebook_uid, current_url, f_name_image_search, path_for_pics, count_photos):
        # search picture on google, parse results, and take a screenshot (in case of a match).
        # try simulating human behaviour to avoid from getting blocked.
        sleep(2)
        google_search_profile_pic()  # Search Google for image (the profile pic)
        sleep(randint(15, 25))
        move_randomly_on_screen(scroll_down=True)  # auto move of mouse, or a press on 'down' key
        self.switch_window()  # switch tab in browser (image search usually opens new tab)
        current_source = self.driver.page_source  # current page source of WebDriver

        # parse page's results after a 'reverse image search' (with Google)
        is_found_on_google = parse_google_image_search(current_source, f_name_image_search, current_url)

        # take a screenshot, if a photo match has been found on web results
        if is_found_on_google:
            optional_keywords = ["Pages that include matching images",
                                 "another pattern to match when there are results"]
            for keyword in optional_keywords:
                if keyword in current_source:  # found matching images to the search
                    # search a keyword on web page, to get a better view for the screenshot
                    pyautogui.hotkey('ctrlleft', 'f')  # shortcut to search a keyword on page
                    sleep(1)
                    pyautogui.typewrite(keyword, interval=0.25)  # search a keyword to find on web page
                    pyautogui.press('esc')  # press 'esc'
                    sleep(1)
                    break
            # screenshot of matching images in Google
            take_a_screenshot(os.path.join(path_for_pics, facebook_uid+"#pic_found_on_google_%d.png") % (count_photos+1))
        sleep(randint(3, 9))

        if "Google" in current_source:  # indicates the browser's window is focused on 'Google'
            pyautogui.hotkey('ctrlleft', 'w')  # close 'Google Search' tab with shortcut
        sleep(2)
        self.switch_window()  # switch tab in browser back
        sleep(2)

        if is_found_on_google:
            return True
        return False

    def target_pics_on_tineye(self):
        # upload & search profiles' pictures, to find matches on Tineye (image search engine)
        sleep(randint(20, 3*60))
        self.reopen_driver(incognito=True)
        self.driver.get("https://www.tineye.com/")
        sleep(randint(3, 4))

        for facebook_uid in self.ids_to_check_on_tineye:
            path_for_pics = os.path.join(PATH_PHOTOS, facebook_uid)
            if os.path.exists(path_for_pics):  # check if dir's path exist
                out_f_name = os.path.join(path_for_pics, facebook_uid+"#profile_pics_on_web.csv")
                pic_files = glob.glob1(path_for_pics, "*.jpg")
                if pic_files:
                    sleep(2)
                    for pic_name in pic_files:
                        sleep(randint(10, 2*60))
                        if self.driver.find_elements_by_id("upload-button"):
                            # click on 'upload-button', to open file dialogue & upload an image
                            self.driver.find_elements_by_id("upload-button")[0].click()
                            sleep(randint(2, 3))
                            # auto uploading of an image to TinEye (using 'pyautogui')
                            upload_image_to_tineye(path_for_pics, pic_name)

                            if self.driver.current_url != "https://www.tineye.com/":
                                sleep(randint(15, 30))
                                current_source = self.driver.page_source  # current page source
                                parse_tineye_results(current_source, out_f_name, pic_name)  # parse search results
                                # auto move of mouse, or a press on 'down' or 'up key
                                move_randomly_on_screen(to_top=True, scroll_up=True, scroll_down=True)

                                sleep(randint(3, 6))
                                if randint(1, 5) == 3:
                                    self.driver.execute_script("window.history.go(-1)")  # back to previous page
                                sleep(2)
        self.driver.delete_all_cookies()

    def scrape_by_command(self, fb_url, command_for_crawler):
        fb_uid = fb_url.replace(FACEBOOK, "").replace(MOBILE_FACEBOOK, "")  # facebook uid from the given url
        if 'exist' in command_for_crawler:
            self.is_target_on_facebook(fb_uid)  # check if profile appears on facebook
        elif 'posts' in command_for_crawler:
            self.scrape_target_posts(fb_url)  # scrape all profile's posts from 'Timeline' section
        elif 'about' in command_for_crawler:
            self.scrape_about_target(fb_url)  # scrapes data about profile from 'About' section
        elif "screenshots" in command_for_crawler:
            self.screenshots_of_target(fb_uid)
        elif "profile_photos" in command_for_crawler:
            self.crawl_target_photos(fb_uid, save_image=True)  # crawl and download profile pictures
        elif "reverse_image_google" in command_for_crawler:
            self.crawl_target_photos(fb_uid, search_image=True)  # crawl and search profile pictures with Google
        else:
            print("Not implemented yet")

    def navigate_by_xpath(self, opt):
        # navigates from the current facebook page to facebook's home page (main page)
        xpath_to_click = HOME_XPATH
        if opt == 'about':
            xpath_to_click = ABOUT_XPATH
        elif opt == 'timeline':
            xpath_to_click = TL_XPATH
        elif opt == 'photos':
            xpath_to_click = PHOTOS_XPATH
        elif opt == 'albums':
            xpath_to_click = ALBUMS_XPATH
        elif opt == 'profile_pics':
            xpath_to_click = PROFILE_PICTURES_XPATH
        try:
            if self.driver.find_elements_by_xpath(xpath_to_click):  # find required button by xpath
                self.driver.find_elements_by_xpath(xpath_to_click)[0].click()  # Clicks 'Home' button
            sleep(randint(2, 4))
        except ElementNotVisibleException:
            print("ElementNotVisibleException")
            pass
        except WebDriverException:
            print("WebDriverException")
            pass


def build_profiles(profile_lst):
    # build profiles by profile list, from existing photos and csv files related to them
    # create docx reports about the profiles from the given list
    for fb_id in profile_lst:
        profile_obj = FbProfile(fb_id)
        profile_obj.profile_to_docx_report()
        sleep(1)


def main():
    """
    The main function (runs the GUI and the Crawler).
    """
    enable_js_preference()  # fix javascript to be enabled on chrome browser
    g = GuiMenu()  # build GuiMenu object
    fb_urls = g.fb_urls  # facebook urls to crawl
    fb_mobile_urls = g.fb_mobile_urls  # facebook urls to crawl in mobile version (when js disabled)

    ids_to_check_on_tineye = []
    if g.check_on_tineye:
        ids_to_check_on_tineye = g.profiles_lst  # profiles to upload & search their photos on TinEye

    if fb_urls or fb_mobile_urls or ids_to_check_on_tineye:
        print(fb_urls)
        print(fb_mobile_urls)
        print(ids_to_check_on_tineye)
        # build 'FacebookCrawler' object
        scraper = FacebookCrawler(fb_urls, fb_mobile_urls, ids_to_check_on_tineye)
        scraper.crawl_all_targets()

    if g.build_profiles and g.profiles_lst:  # build profile is True
        sleep(3)
        build_profiles(g.profiles_lst)

if __name__ == '__main__':
    main()
