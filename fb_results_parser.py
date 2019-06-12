import codecs
import re
import pandas as pd
from program_constants import *
from bs4 import BeautifulSoup

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


def facebook_results_parser(target_url, htm):
    """
    Parse facebook results by target url and page source (html)
    :return:
    """
    fids_lst = parse_ids_from_url(target_url)  # parse facebook profile fid/s from url
    if htm and fids_lst:
        current_date = ret_time_stamp()  # current time in format for time stamp

        columns = ret_cols(target_url)  # set list to use as Dict Keys, and pandas DataFrame's Columns
        raw_data = set_raw_data(columns)  # Dict set with columns for pandas DataFrame

        soup = BeautifulSoup(htm, 'html.parser')  # page source from facebook query search results
        browse_result_elem = soup.find(id="initial_browse_result")  # pages, groups, friends - browse_results
        mutual_friends_elem = soup.find(text="Mutual Friends")

        if mutual_friends_elem or (MUTUAL in target_url):
            # parse mutual friends results
            raw_data = parse_mutual_friends(soup, raw_data, fids_lst, current_date)

        elif browse_result_elem:
            profile_name, profile_name2 = profile_names_from_title(soup, target_url)  # parse profile names
            query = query_from_url(target_url)  # find query in given url
            # parse browse result (groups, pages, friends, followers etc.)
            raw_data = parse_browse_result(query, browse_result_elem, raw_data, fids_lst, profile_name,
                                           profile_name2, current_date)

        if browse_result_elem or mutual_friends_elem:
            # create dirs and filename
            current_date = ret_current_time()  # current time in format for filename
            tmp_path, f_name_q = ret_save_path(target_url)  # Set path to save csv files in
            tmp_file_name = os.path.join(tmp_path, fids_lst[0]+"#"+f_name_q+"#"+current_date+'.csv')  # file name for csv
            if len(fids_lst) == 2:
                tmp_file_name = tmp_file_name.replace(fids_lst[0], fids_lst[0]+"_"+fids_lst[1])
            create_dir(tmp_path)  # create dir in path (if not exist)

            # saves data to csv using pandas
            save_pandas(target_url, soup, columns, raw_data, tmp_file_name, fids_lst, f_name_q)


def query_from_url(target_url):
    # return the query inside the given facebook url (for example: pages-liked)
    for i in range(len(BASIC_Q)):
        if BASIC_Q[i].strip("/") in target_url:
            temp_q = BASIC_Q[i].strip("/")
            return temp_q
    return None


def parse_browse_result(query, results, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse facebook browse result by query (search/fid/groups, search/fid/stories-liked, etc.)
    try:
        if "groups" in query:
            return parse_groups(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
        elif "pages-liked" in query:
            return parse_pages_liked(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
        elif "friends" in query:
            return parse_friends_followers(results, raw_data, fids_lst, profile_name, profile_name2, current_date, "friends")
        elif "followers" in query:
            return parse_friends_followers(results, raw_data, fids_lst, profile_name, profile_name2, current_date, "followers")
        elif "stories" in query:
            return parse_stories(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
        elif "photos" in query:
            return parse_photos(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
        elif "videos" in query:
            return parse_videos(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
        elif "apps" in query:
            return parse_apps_used(results, raw_data, fids_lst, profile_name, profile_name2, current_date)
    except:
        pass


def parse_groups(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from group search results
    for a in soup.find_all('a', href=ret_ref_br_rs):
        if a.find("img"):
            next_elem = find_next_child(a)
            if next_elem:
                group_name, group_link = ret_links_and_names(next_elem)  # parse page's link and name
                members = ret_members(next_elem)  # parse number of likes on page

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[r"Group Name"].append(group_name)  # group name
                raw_data[r"Group ID"].append(group_link)  # group url/id
                raw_data[r"Members"].append(members)  # group members
                raw_data[r"Group Type"].append("Unknown")  # group members
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_pages_liked(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from page search results
    for a in soup.find_all('a', href=ret_ref_br_rs):
        if a.find("img"):
            next_elem = find_next_child(a)
            if next_elem:
                page_name, page_link = ret_links_and_names(next_elem)  # parse page's link and name
                likes = ret_likes(next_elem)  # parse number of likes on page

                # find likes/ranking/page category/place section element
                next_elem = find_page_category_section(next_elem)
                if next_elem:
                    split_by_dot = next_elem.getText().split('·')
                    ranking, page_place, category = ret_ranking_category_and_place(split_by_dot, likes)
                    raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                    raw_data[r"Page Name"].append(page_name)  # page name
                    raw_data[r"Page ID"].append(page_link)  # page url/id
                    raw_data[r"Likes"].append(likes)  # likes on page
                    raw_data[r"Ranking"].append(ranking)  # Ranking on page
                    raw_data[r"Page Place"].append(page_place)  # page place / location
                    raw_data[r"Page Category"].append(category)  # page category ('Health/Beauty' etc.)
                    raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_friends_followers(soup, raw_data, fids_lst, profile_name, profile_name2, current_date, query):
    # parse data from friends OR followers search result, as required (by query)
    name_col = r"Friend Name"
    id_col = r"Friend ID"
    if query == "followers":
        name_col = name_col.replace("Friend", "Follower")
        id_col = id_col.replace("Friend", "Follower")

    for a in soup.find_all('a', href=ret_ref_br_rs):
        if a.find("img"):
            next_elem = find_next_child(a)
            if next_elem:
                friend_name, friend_link = ret_links_and_names(next_elem)  # parse page's link and name
                while len(next_elem) == 1:
                    next_elem = list(next_elem.children)[0]
                details_section = list(next_elem.children)[1]  # detail section element
                details_text = details_section.getText()  # detail section text

                work = ret_detail_with_soup(details_section, "work")  # parse friend's work
                edu = ret_detail_with_soup(details_section, "education")  # parse friend's education
                current_city = ret_detail_with_soup(details_section, "living")  # parse friend's living
                hometown = ret_detail_with_soup(details_section, "hometown")  # parse friend's hometown
                age = ret_detail_with_re(details_text, "age")  # parse friend's age
                gender = ret_detail_with_re(details_text, "gender")  # parse friend's gender
                interest = ret_detail_with_re(details_text, "interest")  # parse friend's interest
                relationship_status = ret_detail_with_re(details_text, "relationship status")  # parse friend's relationship status

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[name_col].append(friend_name)  # friend name
                raw_data[id_col].append(friend_link)  # friend url/id
                raw_data[r"Work"].append(work)  # friend's work
                raw_data[r"Education"].append(edu)  # friend's education
                raw_data[r"Current City"].append(current_city)  # friend's current city
                raw_data[r"Hometown"].append(hometown)  # friend's hometown
                raw_data[r"Age"].append(age)  # friend's age
                raw_data[r"Gender"].append(gender)  # friend's gender
                raw_data[r"Interest"].append(interest)  # friend's interest
                raw_data[r"Relationship Status"].append(relationship_status)  # friend's relationship status
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_stories(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from stories search results
    for a in soup.find_all('a', href=ret_ref_search):
        if a.find("img"):
            story_data_elem = a.parent
            count = 0
            while not (len(story_data_elem.getText()) > 0 and len(list(story_data_elem.children)) >= 3):
                story_data_elem = story_data_elem.parent
                if count > 5:
                    story_data_elem = None
                    break
                count += 1
            # story_data_elem = a.parent.parent.parent
            if story_data_elem:
                # upload_time = ret_upload_time(story_data_elem).replace(",", ";")
                upload_time = ret_upload_time(story_data_elem)  # parse upload time

                headline_elem = list(story_data_elem.children)[0]  # find element with story title
                split_by_dot = headline_elem.getText().split('·')
                # story_title = split_by_dot[0].replace(upload_time, "").replace(",", ";")  # parse story title
                story_title = split_by_dot[0].replace(upload_time, "")
                # story_loc = split_by_dot[1].replace(",", ";")
                story_loc = split_by_dot[1]  # parse story loc
                # parse story text
                # story_text = list(story_data_elem.children)[1].getText().replace(" See More", "").replace(",", ";").replace("\n", " . ")
                story_text = ret_story_text(story_data_elem)  # parse story text
                # story_text = None

                story_comment_section = list(story_data_elem.children)[2]  # find story section of likes/comments/shares
                while len(story_comment_section) == 1:
                    story_comment_section = list(story_comment_section.children)[0]

                comments = comments_from_post(story_comment_section)  # parse story's comments
                shares = shares_from_post(story_comment_section)  # parse story's shares
                likes = likes_from_post(story_comment_section)  # parse story's likes

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[r"Post Title"].append(story_title)  # group name
                raw_data[r"Post Text"].append(story_text)  # group url/id
                raw_data[r"Upload Time"].append(upload_time)  # group members
                raw_data[r"Location"].append(story_loc)  # group members
                raw_data[r"Likes"].append(likes)  # group members
                raw_data[r"Comments"].append(comments)  # group members
                raw_data[r"Shares"].append(shares)  # group members
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_photos(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from photos search results
    for a in soup.find_all('a', href=ref_fb_photo):
        if a.find("img"):
            parent_elem = a.parent  # parent of <a> tag (contain photo and data about it)
            count = 0
            while not (len(parent_elem.getText()) > 0 and len(list(parent_elem.children)) >= 2):
                parent_elem = parent_elem.parent
                if count > 5:
                    parent_elem = None
                    break
                count += 1

            if parent_elem:
                data_section_elem = list(parent_elem.children)[1]  # element with details about photo

                photo_url, photo_src = parse_profile_pic(parent_elem)  # parse photo url&src
                uploader_name, uploader_link = ret_photo_uploader(data_section_elem)  # parse uploader name&link
                likes = ret_photo_likes_comments(data_section_elem, ' like')  # parse likes on photo
                comments = ret_photo_likes_comments(data_section_elem, ' comment')  # parse comments on photo

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[r"Photo URL"].append(photo_url)  # photo url
                raw_data[r"Photo Src"].append(photo_src)  # photo src
                raw_data[r"Uploader Name"].append(uploader_name)  # uploader name
                raw_data[r"Uploader ID"].append(uploader_link)  # uploader link
                raw_data[r"Likes"].append(likes)  # likes
                raw_data[r"Comments"].append(comments)  # comments
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_videos(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from videos search results
    for a in soup.find_all('a', href=ret_href_videos):
        if a.find("img") and a.has_attr('aria-label') and a.has_attr('href') and ('Video' in a['aria-label']):
            parent_elem = a.parent
            count = 0
            while not (len(parent_elem.getText()) > 0 and len(list(parent_elem.children)) >= 3):
                parent_elem = parent_elem.parent
                if count > 5:
                    parent_elem = None
                    break
                count += 1
            # video_data_elem = list(a.parent.parent.parent.children)[2]  # find element that contains video data
            if parent_elem:
                video_data_elem = list(parent_elem.children)[2]

                video_data_text = video_data_elem.getText()  # extract text of 'video_data_elem' element
                video_link = FACEBOOK.replace('.com/', '.com')+a['href']  # parse video link
                video_duration = ret_video_duration(a)  # parse the duration of the video
                uploader_name, uploader_link = ret_links_and_names(video_data_elem)  # parse link and name of uploader
                upload_time = ret_upload_time(video_data_elem)  # parse upload time
                video_title = ret_video_title(video_data_text, uploader_name)  # ret video title
                views = ret_video_views(video_data_text)

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[r"Video Title"].append(video_title)  # Video Title
                raw_data[r"Video Link"].append(video_link)  # Video url/id
                raw_data[r"Uploader Name"].append(uploader_name)  # uploader name
                raw_data[r"Uploader ID"].append(uploader_link)  # uploader id
                raw_data[r"Upload Time"].append(upload_time)  # upload time
                raw_data[r"Views"].append(views)  # views on video
                raw_data[r"Duration"].append(video_duration)  # video duration
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_apps_used(soup, raw_data, fids_lst, profile_name, profile_name2, current_date):
    # parse data from apps-used search results
    for a in soup.find_all('a', href=ret_ref_br_rs):
        if a.find("img"):
            next_elem = find_next_child(a)
            if next_elem:
                app_name, app_link = ret_links_and_names(next_elem)  # parse page's link and name
                app_rating = ret_app_rating(next_elem)
                app_category = ret_app_category(next_elem)

                raw_data = user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2)  # names and user ids
                raw_data[r"App Name"].append(app_name)  # app name
                raw_data[r"App ID"].append(app_link)  # app url/id
                raw_data[r"App Rating"].append(app_rating)  # app rating
                raw_data[r"Category"].append(app_category)  # app category ('News', 'Games', etc.)
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def parse_mutual_friends(soup, raw_data, fids_lst, current_date):
    # parse data from mutual facebook friends results
    div_profile_browser = soup.find("div", {"class": "fbProfileBrowser"})
    if div_profile_browser:  # inner element is found with BeautifulSoup
        soup = div_profile_browser
    if len(fids_lst) == 2:  # 2 facebook profile uids
        for a in soup.find_all('a', href=ret_fref_pb):
            if (not a.find("img")) and len(a.getText()) > 0:
                friend_name = a.getText()  # parse friend name
                friend_link = a['href'].split('fref=pb')[0][:-1]  # parse friend link

                raw_data[r"UID"].append(fids_lst[0])  # facebook uid
                raw_data[r"UID2"].append(fids_lst[1])  # facebook uid2
                raw_data[r"Friend Name"].append(friend_name)  # friend name
                raw_data[r"Friend ID"].append(friend_link)  # friend url/id
                raw_data[r"Time Stamp"].append(current_date)  # current time
    return raw_data


def ret_ref_br_rs(href):
    # find href (with '?ref=br_rs' | '&ref=br_rs'), using regular expression operation
    return href and re.compile(r'(\?|\&)ref=br_rs').search(href)


def ret_ref_search(href):
    # find href (with 'ref=search') using regular expression operation
    return href and re.compile(r'ref=search').search(href)


def ret_fref_pb(href):
    # find href (with 'fref=pb') using regular expression operation
    return href and re.compile(r'fref=pb[^<]hc_location=profile_browser').search(href)


def ref_fb_photo(href):
    # find href (with '/photos/' or 'photo.php?fbid') using regular expression operation
    return href and re.compile(r'(\/photos\/|photo.php\?fbid)').search(href)


def ret_href_videos(href):
    # find href (with '/videos/') using regular expression operation
    return href and re.compile(r'\/videos\/')


def ret_links_and_names(soup):
    # find link and name of <a> tag, by 'href' that contains specific string
    for a_tag in soup.find_all('a', href=ret_ref_br_rs):
        if len(a_tag.getText()) > 0 and not (a_tag.find("img")):
            href = a_tag['href'].replace("/?ref=br_rs", "").replace("/&ref=br_rs", "")
            a_text = a_tag.getText()
            if FACEBOOK[:-1] not in a_tag['href']:
                href = FACEBOOK.replace(".com/", ".com")+href
            return a_text, href
    return None, None


def ret_members(soup):
    # parse groups' members
    for members in soup.find_all(string=re.compile(r'[\d\.KM,]+ member(s|)')):
        if len(members.split(" ")) == 2:
            return members.split(" member")[0]
    return None


def ret_likes(soup):
    # parse pages' likes
    for likes in soup.find_all(string=re.compile(r'[\d\.KM,]+ like(s|) this')):
        if len(likes.split(" ")) == 3:
            return likes.split(" like")[0]
    return None


def find_page_category_section(elem):
    # find element that contains likes/ranking/page category/place section
    while len(elem) == 1:
        elem = list(elem.children)[0]  # traverse down to element's children
    # navigate to element that contains likes/ranking/page category/place section
    elem = list(list(elem.children)[1].children)[0]
    if elem:
        return elem
    return None


def ret_ranking_category_and_place(tmp_lst, likes):
    # find ranking, page place and category of page
    ranking = None
    page_place = None
    page_category = None
    if tmp_lst:
        ranking = ret_page_ranking(likes, tmp_lst[0])  # parse ranking on page
        if len(tmp_lst) > 2:
            page_place = tmp_lst[1]
            page_category = tmp_lst[2]
        elif len(tmp_lst) == 2:
            page_category = tmp_lst[1]
    return ranking, page_place, page_category


def ret_page_ranking(likes, ranking_and_likes):
    # find page ranking
    if likes in ranking_and_likes:
        split_ranking = ranking_and_likes.split(likes)[0]
        if split_ranking:
            return split_ranking
    return None


def ret_detail_with_soup(soup, query):
    # parse friend's details using BeautifulSoup
    re_str = ""
    if query == "work":
        re_str = r' at '
    elif query == "education":
        re_str = r'(Studie|Went to)'
    elif query == "living":
        re_str = r'(Lives in)'
    elif query == "hometown":
        re_str = r'From '
    if re_str:
        for tag in soup.find_all(string=re.compile(re_str)):
            a_tag = tag.parent.find('a', href=True)
            a_text = tag.parent.getText()
            if (query != "work") or (query == "work" and "Studie" not in a_text):
                if a_tag:
                    a_href = a_tag['href']
                    return a_text+" ~ "+a_href
                return a_text
    return None


def ret_detail_with_re(details_text, query):
    # parse friend's details using 're' library
    all_matches = None
    if query == "age":
        all_matches = re.findall(r'[\d\,]+ years old', details_text)  # parse age
    elif query == "gender":
        all_matches = re.findall(r'(Male|Female)', details_text)  # parse gender
    elif query == "interest":
        all_matches = re.findall(r'(Interested in Men|Interested in Women)', details_text)  # parse interest
    elif query == "relationship status":
        for relationship_status in RELATIONSHIP_OPTS:
            gender = re.findall(relationship_status, details_text)  # parse relationship status
            if gender:
                return gender[0]
    if all_matches:
        return all_matches[0]
    return None


def ret_upload_time(soup):
    # parse upload time of post
    for elem in soup.find_all("abbr"):
        if elem.has_attr("data-utime"):
            return elem.getText()
    return None


def ret_story_text(story_data_elem):
    # find the written text/paragraph inside the given element
    elem_text = list(story_data_elem.children)[1].getText()
    if elem_text:
        return elem_text.replace(" See More", "").replace("\n", ". ").replace("\r", ". ")
    return None


def likes_from_post(div):
    # parse likes on post
    for a_tag in div.find_all("a"):  # parse post likes
        if a_tag.has_attr("aria-label") and a_tag["aria-label"].find("See who reacted"):
            return a_tag.getText()
    return None


def comments_from_post(div):
    # parse comments on post
    comments_elem = div.find("a", text=re.compile('[\d\.KM,]+ Comment(s|)'))  # parse post comments
    if comments_elem:
        return comments_elem.getText().split(" Comment")[0]
    return None


def shares_from_post(div):
    # parse shares on post
    shares_elem = div.find("a", text=re.compile('[\d\.KM,]+ Share(s|)'))  # parse post shares
    if shares_elem:
        return shares_elem.getText().split(" Share")[0]
    return None


def ret_photo_uploader(data_section_elem):
    # parse uploader of photo (name&link)
    for tag in data_section_elem.find_all("div"):
        # find element with relevant attributes ('data-bt' and 'snippets')
        if tag.has_attr("data-bt") and ("snippets" in tag["data-bt"]):
            a_tag = tag.find('a', href=True)
            if a_tag and len(a_tag.getText()) > 0:
                uploader_name = a_tag.getText()
                uploader_link = a_tag['href'].replace('?ref=br_rs', "").replace('&ref=br_rs', "")
                if uploader_link[len(uploader_link)-1] == "/":
                    uploader_link = uploader_link[:-1]
                return uploader_name, uploader_link
    return None, None


def ret_photo_likes_comments(data_section_elem, opt):
    # parse likes or comments on photo
    for tag in data_section_elem.find_all("div"):  # parse post likes&comments
        if tag.has_attr('aria-label'):
            aria_label = tag['aria-label']
            if opt in aria_label:
                return aria_label.split(opt)[0]
    return None


def ret_video_duration(a_tag):
    # parse duration of the video from given <a> tag
    if a_tag.has_attr('aria-label'):
        aria_label = a_tag['aria-label']
        if 'Duration: ' in aria_label:
            split_by_duration = aria_label.split('Duration: ')
            if len(split_by_duration) > 1:
                duration = split_by_duration[len(split_by_duration)-1]
                if ('second' in duration.lower()) or ('minute' in duration.lower()) \
                        or ('hour' in duration.lower()):
                    return duration
    return None


def ret_video_views(video_text):
    # parse video views from given text from video element
    video_views_tags = re.findall(r'[\d\.KM,]+ View', video_text)
    if video_views_tags:
        return video_views_tags[0].split(' View')[0]
    return None


def ret_video_title(video_text, uploader_name):
    # split given text from video element (by uploader name), and get the title of the video
    if uploader_name:
        split_video_text = video_text.split(uploader_name)
        if len(split_video_text) > 1:
            video_title = split_video_text[0].replace("\n", ". ").replace("\r", ". ")
            return video_title
    return None


def ret_app_rating(div):
    # parse rating on app
    div_str = str(div)  # change BeautifulSoup element to string
    # find tags that contain rating and reviews on app with regular expression operation
    rating_tags = re.findall(r'data-tooltip-content="([^<]+review(s|))', div_str)
    if rating_tags:
        # first 'group' inside first index from 'rating_tags' (list) - contain a string (app rating)
        app_rating = rating_tags[0][0]
        return app_rating
    return None


def ret_app_category(div):
    # parse app category
    for tag in div.find_all("div"):  # parse post likes
        # find element with relevant attributes ('data-bt' and 'sub_headers')
        if tag.has_attr("data-bt") and ("sub_headers" in tag["data-bt"]):
            tag_text = tag.getText()  # usually contains app rating&category
            if tag_text:
                if 'stars.' in tag_text:
                    return tag_text.split('stars.')[1]
                return tag_text
    return None


def user_and_ids_to_dict(raw_data, fids_lst, profile_name, profile_name2):
    # append facebook profile names and user ids to Dict
    raw_data[r"UID"].append(fids_lst[0])  # facebook user id
    raw_data[r"Profile Name"].append(profile_name)  # facebook profile name
    if len(fids_lst) == 2:
        raw_data[r"UID2"].append(fids_lst[1])  # second facebook user id
        raw_data[r"Profile Name2"].append(profile_name2)  # second profile name
    return raw_data


def parse_ids_from_url(target_url):
    # splits fids from url
    tmp_list = []
    if MUTUAL not in target_url:
        if "--" in target_url:
            if MOBILE_FACEBOOK in target_url:
                tmp_list.append(target_url.strip(MOBILE_FACEBOOK).split("--")[0])
        else:
            for i in target_url.split("/"):
                if i and i.isdigit():
                    tmp_list.append(i)
                    if len(tmp_list) == 2:
                        break
    else:
        tmp_split = target_url.split("=")
        tmp_list.append(tmp_split[1].strip("&node"))
        tmp_list.append(tmp_split[2])
    return tmp_list


def parse_profile_pic(soup_elem):
    # parse profile picture of the facebook profile
    if soup_elem:
        prof_pic_a_tag = soup_elem.find({'a': 'href'})
        if prof_pic_a_tag and prof_pic_a_tag.has_attr('href'):
            prof_pic_link = prof_pic_a_tag['href']
            parent_a = prof_pic_a_tag.parent
            if parent_a:
                prof_pic_elem = parent_a.find({'img': 'src'})  # parse profile picture url
                if prof_pic_elem:
                    prof_pic_url = prof_pic_elem['src']
                    split_url = prof_pic_url.split(".jpg")
                    if len(split_url) > 1:
                        profile_pic = split_url[0]+".jpg"
                        if prof_pic_link:
                            # add facebook url to pic href
                            if FACEBOOK not in prof_pic_link:
                                prof_pic_link = FACEBOOK.replace('.com/', '.com')+prof_pic_link
                            return prof_pic_link, profile_pic
    return None, None


def profile_names_from_title(soup, target_url):
    # parse profile names from page source title (with BeautifulSoup)
    prof_name = None
    prof_name2 = None
    search_title = soup.title.string.split(" - Facebook Search")[0]
    if search_title:
        if INTERSECT in target_url:
            if " and " in search_title:
                split_and = search_title.split(" and ")
                part_str = split_and[0].split(" ")
                prof_name = part_str[len(part_str)-2]+" "+part_str[len(part_str)-1]
                prof_name2 = split_and[1]
            elif ("'s" in search_title) and (" by " in search_title):
                split_s = search_title.split("'s")
                part_str = split_s[0].split(" ")
                prof_name = part_str[len(part_str)-2]+" "+part_str[len(part_str)-1]
                prof_name2 = search_title.split(" by ")[1]
        elif FACEBOOK_SEARCH in target_url:
            if "by" in search_title:
                split_by = search_title.split(" by ")
                prof_name = split_by[1]
            elif "'s" in search_title:
                prof_name = search_title.split("'s")[0]
    return prof_name, prof_name2


def profile_names_from_q_box(soup, target_url):
    # parse profile names from search entry box (with BeautifulSoup)
    prof_name = None
    prof_name2 = None
    search_elem = soup.find("input", {'name': 'q'})
    if search_elem and ('value' in search_elem.attrs):
        search_val = search_elem['value']
        if INTERSECT in target_url:
            if " and " in search_val:
                split_and = search_val.split(" and ")
                part_str = split_and[0].split(" ")
                prof_name = part_str[len(part_str)-2]+" "+part_str[len(part_str)-1]
                prof_name2 = split_and[1]
            elif ("'s" in search_val) and (" by " in search_val):
                split_s = search_val.split("'s")
                part_str = split_s[0].split(" ")
                prof_name = part_str[len(part_str)-2]+" "+part_str[len(part_str)-1]
                prof_name2 = search_val.split(" by ")[1]
        elif FACEBOOK_SEARCH in target_url:
            if "by" in search_val:
                split_by = search_val.split(" by ")
                prof_name = split_by[1]
            elif "'s" in search_val:
                prof_name = search_val.split("'s")[0]
    return prof_name, prof_name2


def find_next_child(a_tag):
    # try to find next child after <a> tag with image, that contains results data (likes, page_category, members .etc)
    parent_elem = a_tag.parent
    count = 0
    while not len(parent_elem.getText()) > 0:
        parent_elem = parent_elem.parent
        if count > 5:
            return None
        count += 1
    if len(list(parent_elem.children)) > 1:
        next_elem = list(parent_elem.children)[1]  # find second child of parent element
        return next_elem
    return None


# TODO add no results for profile without posts
def save_pandas(target_url, soup, columns, raw_data, tmp_file_name, tmp_fids, f_name_q):
    if columns and raw_data:
        # Set Pandas DataFrame with dictionary and columns
        df = pd.DataFrame(raw_data, columns=columns)
        # saves Pandas DataFrame to CSV (if Pandas DF is not empty)
        if not df.empty:
            df.to_csv(tmp_file_name, sep=',', encoding='utf-8-sig', index=False)
        else:
            no_results = soup.find(text="We couldn't find anything for")
            no_results2 = soup.find(text="Looking for people or posts? Try entering a name, "
                                         "location, or different words.")
            no_results3 = soup.find(text="This Page Isn't available")
            if no_results or no_results2 or no_results3:
                tmp_file_name = tmp_file_name.replace(".csv", ".txt")
                with codecs.open(tmp_file_name, 'w', encoding='utf-8') as out_f:
                    out_f.write("No Results, probably because :\n")
                    out_f.write("1) There are no results for the desired query - "+target_url+"\n")
                    if len(tmp_fids) == 1:
                        out_f.write("2) The Profile ["+tmp_fids[0]+"], has no "+f_name_q+" !")
                    elif len(tmp_fids) == 2:
                        out_f.write("The Profiles ["+tmp_fids[0]+"] and ["+tmp_fids[1]+"], has no "+f_name_q
                                    + " in common !")

"""
htm_src = ""
with codecs.open(os.path.join(os.environ["HOMEPATH"], "DESKTOP", "New folder", "test_htm", "htm_apps_used.txt"),
                 'r', encoding='utf-8') as this_file:
    for line in this_file.readlines():
        htm_src += line.strip("\n")

facebook_results_parser("https://www.facebook.com/search/[uid]/apps-used", htm_src)
"""
