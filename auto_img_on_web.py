import codecs
import re
import csv
import pyscreenshot
import pyautogui
from program_constants import *
from bs4 import BeautifulSoup
from time import sleep
from random import randint

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


def parse_google_image_search(source, output_path_name, photo_url):
    # parse google image search results
    res = []
    if source:
        soup = BeautifulSoup(source, 'html.parser')
        if "Google" in soup.title.string:
            soup_text = soup.getText()
            # another pattern to match is optional when browser's language is not set to english
            match_images = re.findall(r'(Pages that include matching images|'
                                      r'another pattern to match when there are results)', soup_text)
            no_google_results = re.findall(r'(No other sizes of this image found|'
                                           r'another pattern to match when there are no results)',
                                           soup_text)

            res.append(photo_url)
            if match_images:
                # another pattern to match is optional when browser's language is not set to english
                google_results = re.findall(r'([\d\.KM,]+ results|[\d\.KM,]+ another pattern for results)', soup_text)
                if google_results:
                    res.append("Found on the web with Google - "+google_results[0]
                               .replace("another pattern for results", "results"))
                else:
                    res.append("Found on the web with Google")
            elif no_google_results:
                res.append("Not found on the web (Google Search)")
            else:
                res.append("couldn't parse image search result (Google Search)")

            save_photo_search_results(output_path_name, res)

            if match_images:
                return True
    return False


def parse_tineye_results(source, output_path_name, pic_name):
    # parse tineye image search results
    res = []
    if source:
        soup = BeautifulSoup(source, 'html.parser')
        search_title = soup.title.string
        photo_search_results = soup.find_all(string=re.compile(r'[\d\.KM,]+ result(s|)'))

        res.append(pic_name)
        if "result" in search_title or "result" in source:
            if ("0 results" in source) or ("0 results" in search_title) \
                    or ("no matches for your image" in source):
                res.append("Not found on the web (TinEye Search)")

            elif search_title and ("result" in search_title) and (" - TinEye" in search_title):
                res.append("Found on the web with TinEye - " +
                           search_title.replace(" - TinEye", "").replace("\n", ""))

            elif photo_search_results:
                res.append("Found on the web with Tineye - " +
                           photo_search_results[0].replace(" - TinEye", "").replace("\n", ""))

        elif "TinEye couldn't reach that webpage" in search_title \
                or "TinEye couldn't reach that webpage" in source:
            res.append("TinEye couldn't reach that webpage!")
        else:
            res.append("couldn't parse image search result (TinEye Search)")

    save_photo_search_results(output_path_name, res)


def save_photo_search_results(output_path_name, res):
    # saves photo search data to csv
    if res:
        with codecs.open(output_path_name, 'a', encoding='utf-8-sig') as out_f:
            tmp_writer = csv.writer(out_f, dialect='excel', delimiter=',', quotechar='"',
                                    skipinitialspace=True)
            if os.stat(output_path_name).st_size == 0:
                tmp_writer.writerow(["Picture Name/Photo URL", "Found On The Web?"])
            tmp_writer.writerow(res)
        out_f.close()


def upload_image_to_tineye(profile_pics_path, pic_name):
    # upload image to TinEye search engine using 'pyautogui'
    pyautogui.press('tab', presses=5, interval=0.25)
    sleep(1)
    pyautogui.press('enter')
    sleep(1)
    pyautogui.typewrite(profile_pics_path, interval=0.25)
    sleep(1)
    pyautogui.press('enter')
    sleep(1)
    pyautogui.press('tab', presses=5, interval=0.25)
    sleep(1)
    pyautogui.typewrite(pic_name, interval=0.25)
    sleep(randint(3, 10))
    pyautogui.press('enter')
    sleep(randint(3, 5))


def find_img_saving_pos(save_image=None, search_image=None, screen_image=None):
    # find good mouse position that enables to: save image as .jpg / reverse search image on google

    if not (save_image or search_image or screen_image):
        return False, None, None

    sleep(1)
    monitor_size = pyautogui.size()  # size of the screen/monitor in pixels
    beginning_pos_x = monitor_size[0]/2+50  # x position near the middle of the monitor
    beginning_pos_y = monitor_size[1]/2+150  # y position near the middle of the monitor

    found_saving_pos = True
    if save_image or search_image:
        found_saving_pos = False
        # loop till getting to the upper-left corner of screen, or find position to save .jpg (not .html) file
        while beginning_pos_x > 50 and beginning_pos_y > 200:
            found_saving_pos = is_pos_to_save_pic(beginning_pos_x, beginning_pos_y)
            if found_saving_pos:  # indicates on a good position to save profile picture
                break
            sleep(2)
            beginning_pos_x -= 150  # decreasing x pos for cursor
            beginning_pos_y -= 50  # decreasing y pos for cursor
            sleep(3)

    sleep(2)
    return found_saving_pos, beginning_pos_x, beginning_pos_y


def is_pos_to_save_pic(x, y):
    # find if current mouse position is good for saving (or reverse image search)
    pyautogui.moveTo(x,  y, 1)  # moving mouse to given pixels on screen
    sleep(1)
    pyautogui.click(button='right')  # right click on image loc
    sleep(1)
    pyautogui.press('down', presses=3, interval=0.25)  # press down three times
    pyautogui.press('enter')  # press enter (to choose 'Save as...' / 'Copy image')
    sleep(2)
    pyautogui.hotkey('ctrlleft', 'c')  # copy '[filename].html' (after save as) or nothing
    sleep(1)

    # hit Win+R shortcut and run notepad++
    pyautogui.hotkey('winleft', 'r')
    sleep(2)
    pyautogui.typewrite('notepad++', interval=0.1)
    pyautogui.press('enter')
    sleep(2)

    # open new text file, paste copied text, and save a temporary text file
    pyautogui.hotkey('ctrlleft', 'n')  # new text file shortcut
    sleep(1)
    pyautogui.hotkey('ctrlleft', 'v')  # paste shortcut
    pyautogui.hotkey('ctrlleft', 'alt', 's')  # save text with notepad++ shortcut
    sleep(1)
    pyautogui.typewrite(os.path.join(DESKTOP_PATH, "tmp_file.txt"), interval=0.1)  # type temp file path&name
    pyautogui.press('enter')  # save the text file
    sleep(1)
    pyautogui.hotkey('ctrlleft', 'w')  # shortcut to close text file window
    sleep(1)
    pyautogui.hotkey('alt', 'f4')  # shortcut to exit notepad++ (all windows)

    # open file and read pasted text using 'pyautogui'
    f = open(os.path.join(os.path.join(DESKTOP_PATH, "tmp_file.txt")), "r+")
    file_line = f.readline()
    f.close()
    remove_temp_file()  # remove the temporary text file

    # '.html' indicates that commands above tried to save the html page (not good position of cursor to save image)
    if '.html' in file_line:
        sleep(2)
        pyautogui.hotkey('alt', 'f4')  # shortcut to close 'Save file...' dialogue (window)
        sleep(1)
        return False
    return True


def move_to_next_profile_pic():
    # move mouse to the center of the screen and press 'right', in order to view next pic (in album)
    monitor_size = pyautogui.size()  # size of the screen/monitor in pixels
    # moving mouse to given pixels on screen
    pyautogui.moveTo(monitor_size[0]/2,  monitor_size[1]/2, 1)
    sleep(randint(2, 5))
    # move to next picture in the album by hitting 'right' key
    pyautogui.press('right')


def save_profile_pic(path_to_save, count_photos):
    # auto save of current profile picture
    pyautogui.click(button='right')  # right click on image loc
    sleep(1)
    pyautogui.press('down', presses=2, interval=0.25)  # press down twice
    sleep(1)
    pyautogui.press('enter')  # press 'Enter' key
    sleep(3)

    if count_photos == 0:
        pyautogui.press('tab', presses=6, interval=0.25)  # press tab 6 times
        sleep(1)
        pyautogui.press('enter')  # press 'Enter' key
        pyautogui.typewrite(path_to_save, interval=0.25)  # type saving path for profile's pics
        pyautogui.press('enter')  # press 'Enter' key
        pyautogui.press('tab', presses=6, interval=0.25)  # press tab 5 times
    pyautogui.press('enter')  # press 'Enter' key to save the profile picture to .jpg file


def google_search_profile_pic():
    # search profile picture on web (with Google), if the mouse hovers on image (on chrome)
    # should press 'right click' on mouse and choose 'Search Google for image' option
    pyautogui.click(button='right')  # right click (should be on image loc)
    sleep(1)
    pyautogui.press('up', presses=2, interval=0.25)  # press down twice
    sleep(1)
    pyautogui.press('enter')  # choose an option, by pressing 'Enter'


def move_randomly_on_screen(to_top=False, scroll_up=False, scroll_down=False):
    # move mouse to the center of the screen and press 'right', in order to view next pic (in album)
    monitor_size = pyautogui.size()  # size of the screen/monitor in pixels

    pos_x = randint(200, monitor_size[0]-200)
    pos_y = randint(200, monitor_size[1]-200)

    sleep(randint(2, 5))
    rand_mouse = randint(1, 6)
    if rand_mouse == 2:
        pyautogui.moveTo(pos_x,  pos_y, randint(2, 5))  # moving mouse to given pixels on screen
        sleep(randint(2, 5))

    if scroll_down:
        rand_down = randint(0, 1)
        if rand_down == 0:
            for i in range(randint(10, 30)):
                pyautogui.keyDown('down')  # keyDown on the key 'down'
        else:
            pyautogui.press('down', presses=randint(3, 8), interval=0.25)  # presses on the key 'down'

    sleep(randint(4, 8))

    if scroll_up:
        sleep(randint(2, 5))
        for i in range(randint(20, 30)):
            pyautogui.keyDown('up')  # keyDown on the key 'up'

    if to_top:
        pyautogui.moveTo(pos_x,  randint(1, 20), randint(2, 5))  # to the top of the screen


def identify_people_in_profile_picture(source, profile_name):
    # use Facebook's 'image recognition' technique to identify people in a profile picture (on Facebook)
    # the contents of the image can be found in page source, using regular expression operation (re library)
    person_in_image = re.findall(r'(Image may contain: (1 person|[\d,]+ people, including %s))' %
                                 profile_name, source)
    if person_in_image:
        return True
    return False


def take_a_screenshot(file_name):
    """
    Grab full screen and save image to file
    If there are problem go to python.exe (and pythonw.exe)->Properties->Compatibility
    ->Override high DPI scaling behaviour...->Choose 'Application'
    """
    # not capture full screen !!!
    im = pyscreenshot.grab()
    im.save(file_name)


def screenshot_by_query(profile_name, query, counter):
    # take screenshot by given path path (with query)
    path_to_create = os.path.join(PATH_SCREENSHOTS, profile_name)
    if 'timeline' in query:
        take_a_screenshot(os.path.join(path_to_create, profile_name+"#timeline_screenshot%d.png" % counter))
    else:
        take_a_screenshot(os.path.join(path_to_create, profile_name+"#"+query,
                                       profile_name+"#%s_screenshot%d.png" % (query, counter)))
