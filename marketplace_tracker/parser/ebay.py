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
    url_request_list = config_handler.read("urls.cfg", "ebay", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        try:
            page = requests.get(request_url, timeout=request_timeout).text
        except Exception:
            logger.error_log("eBay request failed. Request url: " + str(request_url), traceback.format_exc())
            continue

        listing_containers = re.findall(r"data-viewport=.*?</div></li>", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall(r"(?<=class=s-item__link href=)https://www.ebay.\w+/itm/\d+", listing_container)
            thumbnail = re.findall(r"https://i\.ebayimg\.com/images/g/.+?/s-l\d+\.\w+", listing_container)
            title = [*re.findall(r"(?<=alt=\").*?(?=\"></div></a></div>)", listing_container), *re.findall(r"(?<=alt=\').*?(?=\'></div></a></div>)", listing_container)]
            price = re.findall(r"(?<=<span class=s-item__price>).*?(?=</span></div>)", listing_container)
            shipping = [*re.findall(r"(?<=<span class=\"s-item__dynamic s-item__freeXDays\">).*?(?=</span>)", listing_container), *re.findall(r"(?<=<span class=\"s-item__shipping s-item__logisticsCost\">).*?(?=</span>)", listing_container)]
            purchase_option = [*re.findall(r"(?<=<span class=\"s-item__dynamic s-item__purchaseOptionsWithIcon\">).*?(?=</span>)", listing_container), *re.findall(r"(?<=<span class=\"s-item__dynamic s-item__buyItNowOption\">).*?(?=</span>)", listing_container), *re.findall(r"(?<=<span class=\"s-item__purchase-options s-item__purchaseOptions\">).*?(?=</span>)", listing_container)]
            bidcount = re.findall(r"(?<=<span class=\"s-item__bids s-item__bidCount\">).*?(?=</span>)", listing_container)

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

            if len(price) == 1 and len(bidcount) == 0:
                item_info["buy_it_now_price"] = strip_excess_html(price[0])
                item_info["bidding_price"] = ""
            elif len(price) == 1 and len(bidcount) > 0:
                item_info["buy_it_now_price"] = ""
                item_info["bidding_price"] = strip_excess_html(price[0])
            elif len(price) == 2:
                item_info["buy_it_now_price"] = strip_excess_html(price[0])
                item_info["bidding_price"] = strip_excess_html(price[1])
            else:
                item_info["buy_it_now_price"] = ""
                item_info["bidding_price"] = ""

            if len(shipping) > 0:
                item_info["shipping"] = strip_excess_html(shipping[0])
            else:
                item_info["shipping"] = ""

            if len(purchase_option) > 0:
                item_info["purchase_option"] = strip_excess_html(purchase_option[0])
            else:
                item_info["purchase_option"] = ""

            if len(bidcount) > 0:
                item_info["bidcount"] = strip_excess_html(bidcount[0])
            else:
                item_info["bidcount"] = ""

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def strip_excess_html(string):
    return html.unescape(re.sub(r"<.*?>", "", string))