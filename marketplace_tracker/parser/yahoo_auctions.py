import re
import requests
import time
import error_logger
import html

def page_parser(request_delay):
    url_request_list = []
    with open("yahoo_auctions_url_list.txt", "r") as url_request_list_raw:
        url_request_list_lines = url_request_list_raw.readlines()
        url_request_list = list(map(str.strip,url_request_list_lines))

    item_info_list = []
    for request_url in url_request_list:
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0", "Accept-Encoding": "gzip, deflate, br"}
        try:
            page = requests.get(request_url, headers=headers).text.replace("\n", "").replace("\r", "")
        except Exception as e:
            error_logger.error_log("Yahoo Auctions request failed", e)
            continue

        listing_containers = re.findall("<li class=\"Product\">.*?</li>", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall("(?<=href=\")https://page.auctions.yahoo.co.jp/jp/auction/.*?(?=\")", listing_container)
            thumbnail = re.findall("(?<=data-auction-img=\").*?(?=\")", listing_container)
            title = re.findall("(?<=data-auction-title=\").*?(?=\")", listing_container)
            price = re.findall("(?<=<span class=\"Product__label\">現在</span><span class=\"Product__priceValue u-textRed\">).*?(?=</span>)", listing_container)
            buy_now_price = [*re.findall("(?<=span class=\"Product__label\">即決</span><span class=\"Product__priceValue u-textRed\">).*?(?=</span>)", listing_container), *re.findall("(?<=<span class=\"Product__priceValue\">).*?(?=</span>)", listing_container)]
            bidcount = re.findall("(?<=<span class=\"Product__bid\">).*?(?=</span>)", listing_container)
            time_remaining = re.findall("(?<=<span class=\"Product__time\">).*?(?=</span>)", listing_container)

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

            if len(buy_now_price) > 0:
                item_info["buy_now_price"] = strip_excess_html(buy_now_price[0])
            else:
                item_info["buy_now_price"] = ""

            if len(bidcount) > 0:
                item_info["bidcount"] = strip_excess_html(bidcount[0])
            else:
                item_info["bidcount"] = ""

            if len(time_remaining) > 0:
                item_info["time_remaining"] = strip_excess_html(time_remaining[0])
            else:
                item_info["time_remaining"] = ""

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def strip_excess_html(string):
    return html.unescape(re.sub("<.*?>", "", string))