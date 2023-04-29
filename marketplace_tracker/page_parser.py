import re
import requests
import time

def ebay_page_parser(request_delay):
    ebay_url_request_list = []
    with open("ebay_url_list.txt", "r") as ebay_url_request_list_raw:
        ebay_url_request_list_lines = ebay_url_request_list_raw.readlines()
        ebay_url_request_list = list(map(str.strip, ebay_url_request_list_lines))

    item_info_list = []
    for request_url in ebay_url_request_list:
        ebay_page = requests.get(request_url).text
        listing_containers = re.findall("<li data-viewport=.*?</div></li>", ebay_page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall("(?<=class=s-item__link href=)https://www.ebay.com/itm/\d+", listing_container)
            thumbnail = re.findall("https://i\.ebayimg\.com/thumbs/images/g/.+?/s-l225\.jpg", listing_container)
            title = re.findall("(?<=alt=\").*?(?=\"></div></a></div>)", listing_container)
            price = re.findall("(?<=<span class=s-item__price>).*?(?=</span></div>)", listing_container)
            shipping = [*re.findall("(?<=<span class=\"s-item__dynamic s-item__freeXDays\">).*?(?=</span>)", listing_container), *re.findall("(?<=<span class=\"s-item__shipping s-item__logisticsCost\">).*?(?=</span>)", listing_container)]
            purchase_option = [*re.findall("(?<=<span class=\"s-item__dynamic s-item__purchaseOptionsWithIcon\">).*?(?=</span>)", listing_container), *re.findall("(?<=<span class=\"s-item__dynamic s-item__buyItNowOption\">).*?(?=</span>)", listing_container), *re.findall("(?<=<span class=\"s-item__purchase-options s-item__purchaseOptions\">).*?(?=</span>)", listing_container)]
            bidcount = re.findall("(?<=<span class=\"s-item__bids s-item__bidCount\">).*?(?=</span>)", listing_container)

            if len(url) > 0:
                item_info["url"] = strip_excess_html(url[0])
            else:
                continue

            if len(thumbnail) > 0:
                item_info["thumbnail"] = strip_excess_html(thumbnail[0])
            else:
                item_info["thumbnail"] = ""

            if len(title) > 0:
                item_info["title"] = re.sub("&#34;", "\"", strip_excess_html(title[0]))
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
                print(listing_container)
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
    return re.sub("<.*?>", "", string)