import codecs
import re
import csv
from program_constants import *
from fb_results_parser import parse_profile_pic, parse_ids_from_url
from bs4 import BeautifulSoup

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


# TODO add target_url and UID
def parse_about_target(target_url, driver_url, source):
    # Parse profile 'About' section (facebook without javascript version), and save to csv
    current_date = ret_time_stamp()  # current time in format for time stamp
    parsed_ids = parse_ids_from_url(target_url)  # parse facebook user ids in the given url

    if source and parsed_ids:
        fb_user_id = parsed_ids[0]  # facebook user id
        fb_user_name = parse_user_name(driver_url)  # facebook username
        has_phone = parse_has_phone(source)  # parse if profile has phone

        soup = BeautifulSoup(source, 'html.parser')  # BeautifulSoup obj
        prof_name = soup.title.text  # facebook profile name
        # navigate to relevant element (which contains required data about the profile)
        soup = soup.find(id='root')

        prof_pic_link, prof_pic_src = parse_profile_pic(soup)  # parse profile pic url and src
        intro_description = parse_intro_description(soup)  # parse intro description
        education_lst = parse_work_edu_living(soup, 'education')  # parse education places
        work_lst = parse_work_edu_living(soup, 'work')  # parse work places
        living_lst = parse_work_edu_living(soup, 'living')  # parse living places

        contact_lst = parse_contact_basic_info_nicks(soup, 'contact-info', 'Contact Info')  # parse contact info
        basic_info_lst = parse_contact_basic_info_nicks(soup, 'basic-info', 'Basic Info')  # parse basic info
        nicknames_lst = parse_contact_basic_info_nicks(soup, 'nicknames', 'Other Names')  # parse other names or nicknames

        relationship_status = parse_relationship(soup)  # parse relationship status
        family_lst = parse_family(soup)  # parse family members
        prof_bio = pars_bio(soup, prof_name)  # parse written text from bio
        life_events_lst = parse_life_events(soup)  # parse the live events of facebook profile
        favorite_quotes = parse_favorite_quotes(soup)  # parse favorite quotes

        # Order given lists, by given values order
        living_lst, contact_lst, basic_info_lst, nicknames_lst = \
            order_lists_to_organize_data(living_lst, contact_lst, basic_info_lst, nicknames_lst)

        # append values (using append/append_values func) to 'parsed_data' (list)
        parsed_data = fill_parsed_data(fb_user_id, fb_user_name, prof_name, prof_pic_link, prof_pic_src, has_phone,
                                       intro_description, education_lst, work_lst, living_lst, contact_lst,
                                       basic_info_lst, nicknames_lst, relationship_status, family_lst,
                                       prof_bio, life_events_lst, favorite_quotes, current_date)

        # Saves all parsed data to a csv file
        save_about_data_to_csv(parsed_data)


def parse_has_phone(source):
    # parse if profile is available on his phone (It means that the person has phone)
    has_phone = None
    available_all = re.findall(r'aria-label="([^<]+is available on[^<]+phone)', source)
    if available_all:
        has_phone = available_all[0]
    return has_phone


def parse_user_name(url):
    # parse facebook username from current url of WebDriver (profile's 'About' page)
    fb_user_name = None
    if ('/about' in url) and (MOBILE_FACEBOOK in url):
        split_driver_url = url.split(MOBILE_FACEBOOK)[1].split('/about')[0]  # split url, search for username
        if 'profile.php?id=' not in split_driver_url:
            fb_user_name = split_driver_url
    return fb_user_name


def parse_intro_description(soup):
    # Parse Intro Quote
    prof_pic_a_tag = soup.find({'a': 'href'})
    into_quot_elem = prof_pic_a_tag.parent.parent.next_sibling
    if into_quot_elem and len(into_quot_elem.getText()) > 0:
        return into_quot_elem.getText().replace("\n", ". ").replace("\r", ". ")
    return None


def parse_work_edu_living(soup, query_id):
    # parse all 'work', 'education' and 'living' places - By query 'id' for 'soup.find'
    tmp_lst = []
    work_div = soup.find('div', {'id': query_id})
    if work_div:
        for a_tag in work_div.find_all('a'):
            if (a_tag.has_attr('href')) and (len(a_tag.getText()) > 0):
                if query_id == 'living':
                    living_type_elem = a_tag.parent.parent.previous_element
                    living_type = ""
                    if living_type_elem:
                        if "Current City" in living_type_elem:
                            living_type = "Current City ~ "
                        elif "Hometown" in living_type_elem:
                            living_type = "Hometown ~ "
                    tmp_lst.append(living_type+FACEBOOK+a_tag['href'].strip('/')+" ~ "+a_tag.getText())
                else:
                    tmp_lst.append(FACEBOOK+a_tag['href'].strip('/')+" ~ "+a_tag.getText())
    return tmp_lst


def parse_contact_basic_info_nicks(soup, query_id, text_q):
    # parse 'Contact Info', 'Basic Info' and 'Other Names' - By query 'id' for 'soup.find'
    tmp_lst = []
    div_elem = soup.find('div', {'id': query_id})
    if div_elem:
        for tr_elem in div_elem.find_all('tr'):
            if (text_q not in tr_elem.getText()) and len(tr_elem) == 2:
                res = ""
                for td in tr_elem:
                    a_tag = td.find('a')
                    if res:
                        if a_tag and len(a_tag.getText()) > 0:
                            if 'Websites' not in a_tag.getText():
                                res += " ~ "+FACEBOOK+a_tag['href'].strip("/")+" ~ "+a_tag.getText()
                            else:
                                res += " ~ "+a_tag.getText()
                        else:
                            res += " ~ "+td.getText()
                    else:
                        res += td.getText()
                if res:
                    tmp_lst.append(res)
    return tmp_lst


# TODO notice that this piece of cod was changed
def parse_relationship(soup):
    # parse relationship status of profile
    relationship_div = soup.find('div', {'id': 'relationship'})
    # relationship_opts = ["Single", "Married", "Divorced", "It's complicated", "In a relationship", "Engaged",
    # "In a civil union", "In an open relationship", "Separated", "Widowed", "In a domestic relationship"]
    if relationship_div:
        relationship_status = relationship_div.getText()
        if relationship_status:
            """
            for index in relationship_opts:
                if index in relationship_opts:
                    return index
            """
            return relationship_status.replace("Relationship", "")
    return None


def parse_family(soup):
    # parse family members of profile
    family_arr = []
    family_div = soup.find('div', {'id': 'family'})
    if family_div:
        family_elems = family_div.find_all('h3')
        if family_elems and len(family_elems) % 2 == 0:
            c = 0
            res = ""
            for h3 in family_elems:
                a_tag = h3.find('a')
                # print(a_tag, "\n*********\n")
                if a_tag and a_tag.has_attr('href'):
                    # if a_tag and len(a_tag.getText()) > 0:
                    res += FACEBOOK+a_tag['href'].strip("/")+" ~ "+h3.getText()
                else:
                    res += " ~ "+h3.getText()
                c += 1
                if c % 2 == 0:
                    family_arr.append(res)
                    res = ""
    return family_arr


def pars_bio(soup, prof_name):
    # parse bio section of profile
    bio_div = soup.find('div', {'id': 'bio'})
    if bio_div:
        bio_text = bio_div.getText()
        if bio_text:
            if prof_name and prof_name.split(" "):
                bio_text = bio_text.replace("About "+prof_name.split(" ")[0], "")
            return bio_text.replace("\n", ". ").replace("\r", ". ")
    return None


def parse_life_events(soup):
    # parse 'Life Events' from profile
    events_arr = []
    life_events_div = soup.find('div', {'id': 'year-overviews'})
    if life_events_div:
        event_images = life_events_div.find_all({'img': 'src'})
        if event_images:
            for event_img in event_images:
                event_div = event_img.parent
                if event_div:
                    res = ""
                    # parse year elem
                    event_year_elem = event_div.previous_sibling
                    while event_year_elem:  # loop till find the year of life event
                        if event_year_elem.getText().isdigit():  # the digits indicate year (ex. '2002')
                            res += event_year_elem.getText()+" ~ "
                            break
                        event_year_elem = event_year_elem.previous_sibling
                    # parse life event and link of the relevant post
                    for a_tag in event_div.find_all('a'):
                        if (a_tag.has_attr('href')) and (len(a_tag.getText()) > 0):
                            res += FACEBOOK.replace('.com/', '.com')+a_tag['href'] + " ~ "+a_tag.getText()
                    events_arr.append(res)
    return events_arr


def parse_favorite_quotes(soup):
    # parse Favorite Quotes of profile
    fav_quotes_div = soup.find('div', {'id': 'quote'})
    if fav_quotes_div:
        fav_quotes_text = fav_quotes_div.getText()
        if fav_quotes_text:
            fav_quotes_text = fav_quotes_text.replace("Favorite Quotes", "").\
                replace("\n", ". ").replace("\r", ". ")
            return fav_quotes_text
    return None


def append_values(given_lst, parsed_data, max_length):
    # append values from 'given_list' (list) to 'parsed_data' (list),
    # or 'None (where data is missed) - in range of given 'max_length'
    for i in range(max_length):  # max range - to append data in order to keep csv data organized
        if i < len(given_lst):
            parsed_data.append(given_lst[i])  # append current value of 'given_lst' to 'parsed_data'
        else:
            parsed_data.append(None)  # append 'None' to 'parsed_data' if required value is missed
    return parsed_data


def fill_parsed_data(fb_user_id, fb_user_name, prof_name, prof_pic_link, prof_pic_src, has_phone,
                     intro_description, education_lst, work_lst, living_lst, contact_lst,
                     basic_info_lst, nicknames_lst, relationship_status, family_lst,
                     prof_bio, life_events_lst, favorite_quotes, current_date):
    # append values (using append/append_values func) to 'parsed_data' (list),
    # by columns order of the output csv

    # initialize 'parsed_data' (list) with given values
    parsed_data = [fb_user_id, fb_user_name, prof_name, prof_pic_link,
                   prof_pic_src, has_phone, intro_description]
    # append values (using append/append_values func) to 'parsed_data'
    parsed_data = append_values(education_lst, parsed_data, 6)  # append 6 columns for Education, from other list
    parsed_data = append_values(work_lst, parsed_data, 6)  # append 6 columns for Work, from other list
    parsed_data = append_values(living_lst, parsed_data, 2)  # append 2 columns (Current City, Hometown)
    parsed_data = append_values(contact_lst, parsed_data, 15)  # append 15 columns for contact info, from other list
    parsed_data = append_values(basic_info_lst, parsed_data, 9)  # append 9 columns for basic info, from other list
    parsed_data = append_values(nicknames_lst, parsed_data, 12)  # append 12 columns for other names, from other list
    parsed_data.append(relationship_status)  # append relationship status (for example: Engaged)
    parsed_data = append_values(family_lst, parsed_data, 10)  # append 12 columns for family members, from other list
    parsed_data.append(prof_bio)  # append profile's bio
    parsed_data = append_values(life_events_lst, parsed_data, 6)  # append 6 columns for life events, from other list
    parsed_data.append(favorite_quotes)  # append favorite quotes
    parsed_data.append(current_date)
    return parsed_data  # return 'parsed_data_ list with all required values


def order_lists_to_organize_data(living_lst, contact_lst, basic_info_lst, nicknames_lst):
    # Order given lists, by given values order - so columns in the csv file will remain ordered as required

    living_lst = order_list(living_lst, [r"Current City", r"Hometown"])
    contact_lst = order_list(contact_lst, [r"Phone", r"Email", r"Facebook", r"Instagram", r"Twitter", r"Snapchat",
                                           r"Youtube", r"LinkedIn", r"Skype", r"Websites", r"Websites"])
    basic_info_lst = order_list(basic_info_lst, [r"Birthday", r"Gender", r"Interested In",
                                                 r"Languages", r"Religious Views", r"Political Views"])
    nicknames_lst = order_list(nicknames_lst, [r"Nickname", r"Nickname", r"Maiden Name", r"Alternative Name",
                                               r"Married Name", r"Father's Name", r"Birth Name", r"Former Name",
                                               r"Name With Title", r"Other", r"Other", r"Other"])
    return living_lst, contact_lst, basic_info_lst, nicknames_lst


def order_list(given_lst, values):
    # order given list, by required given values
    ordered_lst = []
    if given_lst:
        for i in range(len(values)):
            if given_lst:
                # search for appearance of current value in the given list, and append it to ordered list
                given_lst, ordered_lst = ret_value_from_list(given_lst, ordered_lst, values[i])
            else:
                ordered_lst.append(None)  # append 'None' to ordered list if given list is empty
    return ordered_lst


def ret_value_from_list(given_lst, ordered_lst, val_name):
    # find required value in the list
    value_found = False
    for i in range(len(given_lst)):
        if val_name in given_lst[i]:
            if " ~ " in given_lst[i]:
                split_lst = given_lst[i].split(" ~ ")  # value with sections separated by '~'
                if '/' not in split_lst[0]:
                    ordered_lst.append(given_lst[i].replace(split_lst[0]+" ~ ", ""))  # append value to ordered list
                else:
                    ordered_lst.append(given_lst[i])  # append value to ordered list
            else:
                ordered_lst.append(given_lst[i])  # append value to ordered list
            given_lst.pop(i)  # pop value from given list
            value_found = True
            break
    # append 'None' to ordered list if value not found
    if not value_found:
        ordered_lst.append(None)
    # return given and ordered list (after changes)
    return given_lst, ordered_lst


def save_about_data_to_csv(parsed_data):
    """
    :param parsed_data: list
    """
    if parsed_data:
        create_dir(PATH_ABOUT)
        tmp_file_name = os.path.join(PATH_ABOUT, 'about_targets.csv')

        with codecs.open(tmp_file_name, 'a', encoding='utf-8-sig') as out_f:
            tmp_writer = csv.writer(out_f, dialect='excel', delimiter=',', quotechar='"',
                                    skipinitialspace=True)
            if os.stat(tmp_file_name).st_size == 0:
                tmp_writer.writerow(ABOUT_COL)
            tmp_writer.writerow(parsed_data)
        out_f.close()

"""
from time import sleep
for i in range(4):
    sleep(3)
    this_path = os.path.join(os.environ["HOMEPATH"], "DESKTOP", "test_htm", "About Htms", "htm%s.txt" % str(i+1))
    htm_src = ""
    with codecs.open(this_path, 'r', encoding='utf-8') as out_f:
        for line in out_f.readlines():
            htm_src += line.strip("\n")
    out_f.close()

    parse_about_target("https://mbasic.com/[uid]",
                       "https://mbasic.facebook.com/profile.php?id=[uid]/about", htm_src)
"""
