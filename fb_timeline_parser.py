import re
from program_constants import *
from bs4 import BeautifulSoup
from fb_results_parser import comments_from_post, shares_from_post, parse_ids_from_url, save_pandas
# import codecs
# import re
# import pandas as pd

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


# TODO - add tagged profiles, profile url. profile pic
def parse_target_posts(target_url, all_htm):
    # Parse profile posts from timeline (facebook without javascript version), and save to csv
    tmp_list = parse_ids_from_url(target_url)
    if all_htm and tmp_list:
        fb_id = tmp_list[0]  # profile fid
        soup = BeautifulSoup(all_htm[0], 'html.parser')  # first page from timeline (contains details on profile)
        profile_name = soup.title.string  # The profile name usually appears in page source title

        tmp_path, f_name_q = ret_save_path(target_url+"--posts")  # Set path to save csv files in
        current_date = ret_current_time()  # current time in format for filename
        tmp_file_name = os.path.join(tmp_path, fb_id+"#"+f_name_q+"#"+current_date+'.csv')  # file name for csv
        create_dir(tmp_path)  # create dir in path (if not exist)

        current_date = ret_time_stamp()  # current time in format for time stamp
        columns = ret_cols(target_url+"--posts")  # columns for csv file
        raw_data = set_raw_data(columns)  # dict set with columns

        # Iterate parsing process of timeline posts, and store parsed data In a CSV file (with pandas)
        for htm in all_htm:
            soup = BeautifulSoup(htm, 'html.parser')
            tl_feed_elem = soup.find("div", {"id": "tlFeed"})
            if tl_feed_elem:
                articles_elems = tl_feed_elem.find_all("div", {"role": "article"})  # Find posts' data from source
                if articles_elems:
                    for div in articles_elems:
                        div_text = div.getText()
                        if div_text and (profile_name in div_text):
                            title_elem = div.find("h3")
                            if title_elem:
                                post_title = title_elem.getText()
                                p_tags = div.find_all("p")  # parse written paragraphs from post
                                status_text, status_hashtags, status_links = text_and_links_from_post(p_tags)
                                # append parsed data to dictionary
                                raw_data[r"UID"].append(fb_id)  # Facebook user id
                                raw_data[r"Profile Name"].append(profile_name)  # Facebook profile name
                                raw_data[r"Post Title"].append(post_title)  # Post title
                                raw_data[r"Post Text"].append(status_text)  # written text inside post
                                raw_data[r"Upload Time"].append(upload_time_from_post(div))  # status upload time
                                raw_data[r"CheckIn"].append(location_from_post(title_elem))  # check-in inside post
                                raw_data[r"Hashtags"].append(status_hashtags)  # hashtags inside post
                                raw_data[r"Links"].append(status_links)  # links inside post
                                raw_data[r"Tagged People"].append(None)  # people tagged in post
                                raw_data[r"Likes"].append(likes_from_post(div))  # num of likes on post
                                raw_data[r"Comments"].append(comments_from_post(div))  # num of comments on post
                                raw_data[r"Shares"].append(shares_from_post(div))  # num of shares on post
                                raw_data[r"Photo Src"].append(photo_url_from_post(div))  # url of photo inside post
                                raw_data[r"Post Type"].append(post_type_from_post(post_title, profile_name))  # post type
                                raw_data[r"Time Stamp"].append(current_date)  # current date and time

        save_pandas(target_url, soup, columns, raw_data, tmp_file_name, [fb_id], f_name_q)


def photo_url_from_post(div):
    # parse photo url from post
    photo_elem = div.find('img')  # parse photo url from post
    if photo_elem:
        split_photo_url = photo_elem['src'].split(".jpg")
        if len(split_photo_url) > 1:
            status_photo = split_photo_url[0]+".jpg"
            return status_photo
    return None


def post_type_from_post(post_title, profile_name):
    # return post type by post title (for example: cover photo update)
    post_type = "post"
    if 'profile picture' in post_title:
        post_type = "profile picture update"
    elif 'cover photo' in post_title:
        post_type = "cover photo update"
    elif 'shared' in post_title:
        post_type = "shared post"
        if 'link' in post_title:
            post_type = "shared link"
        elif 'photo' in post_title:
            post_type = "shared photo"
        elif 'video' in post_title:
            post_type = "shared video"
    elif 'with '+profile_name in post_title:
        post_type = "post that tagged the profile"
        if 'others' in post_title:  # more than ten people tagged
            post_type += " and other people"
    elif (profile_name+" is" in post_title) and (" with" in post_title):
        post_type = "post by profile that tagged others"
    return post_type


def location_from_post(title_elem):
    # parse check-in inside the element of post
    status_loc_elem = title_elem.find(text=re.compile(' at '))  # parse check-in from post
    if status_loc_elem:
        a_tags_in_title = title_elem.find_all('a', href=True)
        if a_tags_in_title:
            location_elem = a_tags_in_title[len(a_tags_in_title)-1]
            if location_elem and ('href' in location_elem.attrs):
                return location_elem.getText()+" ~ "+location_elem['href']
    return None


def text_and_links_from_post(p_tags):
    # parse written text, and links/hashtags inside post
    status_text = ""
    status_hashtags = ""
    status_links = ""
    if p_tags:
        for p in p_tags:
            status_text += p.getText()+"\n"  # parse post text from <p>
            links = p.find_all('a')
            if links:
                for link in links:
                    if 'href' in link.attrs:
                        href = link['href']
                        link_text = link.getText().replace("\n", ". ").replace("\r", ". ")
                        if link_text and ('#' in link_text):
                            status_hashtags += link_text+" · "  # parse hashtag from <a>
                        else:
                            status_links += link_text+" ~ "+href+" · "  # parse link from <a>
    if status_hashtags:
        status_hashtags = status_hashtags[:-3]
    if status_links:
        status_links = status_links[:-3]
    return status_text, status_hashtags, status_links


def upload_time_from_post(div):
    # parse upload time of post
    upload_time_elem = div.find("abbr")  # parse post upload time
    if upload_time_elem and upload_time_elem.getText():
        return upload_time_elem.getText()
    return None


def likes_from_post(div):
    # parse likes on post
    for a_tag in div.find_all('a', href=True):
        if a_tag.has_attr('aria-label'):
            likes_elem = a_tag['aria-label']
            if "including Like" in likes_elem:
                return likes_elem
    return None
"""
import codecs
htm_src = ""
with codecs.open(os.path.join(os.environ["HOMEPATH"], "DESKTOP", "test_htm", "posts_htm",
                              "htm_posts1.txt"),
                 'r', encoding='utf-8') as this_file:
    for line in this_file.readlines():
        htm_src += line.strip("\n")

parse_target_posts(MOBILE_FACEBOOK+"[uid]", [htm_src])
"""
