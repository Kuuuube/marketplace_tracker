import json
import re
import requests
import time
import error_logger
import config_handler

def page_parser(request_delay):
    url_request_list = config_handler.read("urls.cfg", "blocket", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        raw_url_params = re.findall("\?.*", request_url)
        url_params = ""
        if len(raw_url_params) > 0:
            url_params = raw_url_params[0]
        else:
            continue

        headers = {"Authorization": "Bearer " + generate_token()}
        try:
            page = requests.get("https://api.blocket.se/search_bff/v2/content" + url_params, headers=headers)
        except Exception as e:
            error_logger.error_log("Blocket request failed", e)
            continue

        try:
            json_listings = json.loads(page.text)["data"]
        except Exception as e:
            error_logger.error_log("Blocket json invalid: " + page.text, e)
            continue

        for listing in json_listings:
            item_info = {}
            url = try_json("share_url", json_file=listing)
            thumbnail = try_json("images", 0, "url", json_file=listing)
            title = try_json("subject", json_file=listing)
            price = try_json("price", "value", json_file=listing) + " " + try_json("price", "suffix", json_file=listing)

            item_info["url"] = url
            item_info["thumbnail"] = thumbnail
            item_info["title"] = title
            item_info["price"] = price

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def try_json(*keys, json_file):
    try:
        current_json = json_file
        for key in keys:
            current_json = current_json[key]
        return str(current_json)
    except Exception as e:
        error_logger.error_log("Blocket json keys invalid: " + str(keys), e)
        return ""

def generate_token():
    try:
        return json.loads(requests.get("https://www.blocket.se/api/adout-api-route/refresh-token-and-validate-session").text)["bearerToken"]
    except Exception as e:
        error_logger.error_log("Blocket token generation failed", e)