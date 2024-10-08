import json
import re
import requests
import time
import traceback
import logger
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay, request_timeout):
    url_request_list = config_handler.read("urls.cfg", "blocket", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        raw_url_params = re.findall(r"\?.*", request_url)
        url_params = ""
        if len(raw_url_params) > 0:
            url_params = raw_url_params[0]
        else:
            continue
        token = generate_token(request_timeout)
        if token == None:
            continue
        headers = {"Authorization": "Bearer " + token}
        try:
            page = requests.get("https://api.blocket.se/search_bff/v2/content" + url_params, headers=headers, timeout=request_timeout)
        except Exception:
            logger.error_log("Blocket request failed. Request url: " + str(request_url) + ", Request headers: " + str(headers), traceback.format_exc())
            continue

        try:
            json_listings = json.loads(page.text)["data"]
        except Exception:
            logger.error_log("Blocket json invalid: " + page.text + ", Status code: " + str(page.status_code) + ", Headers: " + str(page.headers), traceback.format_exc())
            continue

        for listing in json_listings:
            item_info = {}
            url = try_json("share_url", json_file=listing)
            thumbnail = try_json_unhandled("images", 0, "url", json_file=listing) #thumbnail is not required for blocket listings, failure to find a thumbnail should not log an error
            title = try_json("subject", json_file=listing)
            if "price" in listing: #not all blocket listings will have price, this is not an error
                price = try_json("price", "value", json_file=listing) + " " + try_json("price", "suffix", json_file=listing)
            else:
                price = ""

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
    except Exception:
        logger.error_log("Blocket json keys invalid: " + str(keys) + ", json file: " + str(json_file), traceback.format_exc())
        return ""

def try_json_unhandled(*keys, json_file):
    try:
        current_json = json_file
        for key in keys:
            current_json = current_json[key]
        return str(current_json)
    except Exception:
        return ""

def generate_token(request_timeout):
    try:
        return json.loads(requests.get("https://www.blocket.se/api/adout-api-route/refresh-token-and-validate-session").text, timeout=request_timeout)["bearerToken"]
    except Exception:
        logger.error_log("Blocket token generation failed", traceback.format_exc())
