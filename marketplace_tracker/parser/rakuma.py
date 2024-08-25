import re
import requests
import time
import logger
import html
import traceback
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay, request_timeout):
    url_request_list = config_handler.read("urls.cfg", "rakuma", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        try:
            page = requests.get(request_url, timeout=request_timeout).text.replace("\n", "").replace("\r", "")
        except Exception:
            logger.error_log("Rakuma request failed. Request url: " + str(request_url), traceback.format_exc())
            continue

        listing_containers = re.findall("<div class=\"item\">.*?class=\"like_item_off\">", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall("(?<=<a href=\")https://item.fril.jp/\\w+", listing_container)
            thumbnail = re.findall("(?<=<img src=\").*?(?=\")", listing_container)
            title = re.findall("(?<=class=\"link_search_title\" title=\").*?(?=\" onclick)", listing_container)
            price = re.findall("(?<=<p class=\"item-box__item-price\"><span data-content=\"JPY\">¥</span><span data-content=\").*?(?=\")", listing_container)

            if len(url) > 0:
                item_info["url"] = strip_excess_html(url[0])
            else:
                continue

            if len(thumbnail) > 1:
                item_info["thumbnail"] = strip_excess_html(thumbnail[1])
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