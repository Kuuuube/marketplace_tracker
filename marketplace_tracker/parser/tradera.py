import html
import re
import requests
import time
import error_logger
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay):
    url_request_list = config_handler.read("urls.cfg", "tradera", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        try:
            page = requests.get(request_url).text
        except Exception as e:
            error_logger.error_log("Tradera request failed. Request url: " + str(request_url), e)
            continue

        listing_containers = re.findall("<div id=\"item-card.*?</div></div></div></div></div>", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall("(?<=href=\")/item/.*?(?=\">)", listing_container)
            thumbnail = re.findall("(?<=<img loading=\"lazy\" src=\").*?(?=\")", listing_container)
            title = re.findall("(?<=<a title=\").*?(?=\")", listing_container)
            price = re.findall("(?<=<span class=\"text-nowrap font-weight-bold font-hansen\" data-testid=\"price\">).*?(?=</span>)", listing_container)
            buy_it_now_price = re.findall("(?<=<span class=\"text-nowrap text-inter-light\" data-testid=\"bin-price\">).*?(?=</span>)", listing_container)
            buy_it_now_label = re.findall("(?<=<span data-testid=\"fixedPriceLabel\" class=\"text-nowrap\">).*?(?=</span>)", listing_container)
            bidcount = re.findall("(?<=<span class=\"text-nowrap\">).*?(?=</span>)", listing_container)

            if len(url) > 0:
                item_info["url"] = "https://www.tradera.com" + (url[0])
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

            if len(buy_it_now_price) > 0:
                item_info["buy_it_now_price"] = strip_excess_html(buy_it_now_price[0])
            else:
                item_info["buy_it_now_price"] = ""

            if len(buy_it_now_label) > 0:
                item_info["buy_it_now_label"] = strip_excess_html(buy_it_now_label[0])
            else:
                item_info["buy_it_now_label"] = ""

            if len(bidcount) > 0:
                item_info["bidcount"] = strip_excess_html(bidcount[0])
            else:
                item_info["bidcount"] = ""

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def strip_excess_html(string):
    return html.unescape(re.sub("<.*?>", "", string))