import json
import re
import requests
import time
import error_logger
import config_handler

def page_parser(request_delay):
    url_request_list = config_handler.read("urls.cfg", "mercari_us", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        headers = {"User-Agent": "Mercari_w/1 (Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0)"}
        params = {"operationName": "searchFacetQuery"}
        extensions = {"persistedQuery":{"version":1, "sha256Hash":"5b7b667eaf8a796406058428fa5df18e7cecd5229702ee0753a091d980884d38"}}
        variables = {
            "criteria": {
                "offset": 0,
                "soldItemsOffset": 0,
                "promotedItemsOffset": 0,
                "sortBy": 0,
                "length": 30,
                "query": "",
                "itemConditions": [],
                "shippingPayerIds": [],
                "sizeGroupIds": [],
                "sizeIds": [],
                "itemStatuses": [],
                "customFacets": [],
                "facets": [1,2,3,5,7,8,9,10,11,13],
                "authenticities": [],
                "deliveryType": "all",
                "state": None,
                "locale": None,
                "shopPageUri": None,
                "withCouponOnly": None,
                "minPrice": None,
                "maxPrice": None,
                "colorIds": [],
                "categoryIds": []
            },
            "categoryId": 0
        }
        
        raw_url_params = re.findall("(?<=\?).*", request_url)
        if len(raw_url_params) > 0:
            for raw_url_param in raw_url_params[0].split("&"):
                raw_url_param_eq_split = raw_url_param.split("=")

                if raw_url_param_eq_split[0] == "keyword":
                    raw_url_param_eq_split[0] = "query"
                elif "-" in raw_url_param_eq_split[1]:
                    print("Unsupported param " + str(raw_url_param_eq_split[0]) + " found, list params are not supported, ignoring param")
                    continue
                elif raw_url_param_eq_split[0] not in variables["criteria"].keys():
                    print("Unsupported param " + str(raw_url_param_eq_split[0]) + " found, ignoring param")
                    continue

                if raw_url_param_eq_split[1].isdigit():
                    variables["criteria"][raw_url_param_eq_split[0]] = int(raw_url_param_eq_split[1])
                else:
                    variables["criteria"][raw_url_param_eq_split[0]] = raw_url_param_eq_split[1]

            params["variables"] = json.dumps(variables)
            params["extensions"] = json.dumps(extensions)

        else:
            continue

        try:
            page = requests.get("https://www.mercari.com/v1/api", params=params, headers=headers)
        except Exception as e:
            error_logger.error_log("Mercari US request failed", e)
            continue

        try:
            json_listings = json.loads(page.text)["data"]["search"]["itemsList"]
        except Exception as e:
            error_logger.error_log("Mercari US json invalid: " + page.text, e)
            continue

        for listing in json_listings:
            item_info = {}
            url = "https://www.mercari.com/us/item/" + try_json("id", json_file=listing)
            thumbnail = try_json("photos", 0, "thumbnail", json_file=listing)
            title = try_json("name", json_file=listing)
            price = try_json("price", json_file=listing)

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
        return current_json
    except Exception as e:
        error_logger.error_log("Mercari US json keys invalid: " + str(keys), e)
        return ""