import re
import requests
import time
import error_logger
import html
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay):
    url_request_list = config_handler.read("urls.cfg", "rakuma", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        try:
            page = requests.get(request_url).text.replace("\n", "").replace("\r", "")
        except Exception as e:
            error_logger.error_log("Rakuma request failed. Request url: " + str(request_url), e)
            continue

        listing_containers = re.findall("<div class=\"item\">.*?<div class=\"item-box__like_area\">", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall("(?<=<a href=\")https://item.fril.jp/\w+", listing_container)
            thumbnail = re.findall("(?<=<meta itemprop=\"image\" content=\").*?(?=\">)", listing_container)
            title = re.findall("(?<=<span itemprop=\"name\">).*?(?=</span>)", listing_container)
            price = re.findall("(?<=<span itemprop=\"price\" data-content=\").*?(?=\">)", listing_container)

            if len(url) > 0:
                item_info["url"] = strip_excess_html(url[0])
            else:
                continue

            if len(thumbnail) > 0:
                item_info["thumbnail"] = strip_excess_html(thumbnail[0])
            else:
                item_info["thumbnail"] = ""

            if len(title) > 0:
                item_info["title"] = strip_excess_html(title[0])
            else:
                item_info["title"] = ""

            if len(price) > 0:
                item_info["price"] = strip_excess_html(price[0])
            else:
                item_info["price"] = ""

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def strip_excess_html(string):
    return html.unescape(re.sub("<.*?>", "", string))