import cryptography.hazmat.primitives.asymmetric.ec, cryptography.hazmat.primitives.asymmetric.utils, cryptography.hazmat.primitives.hashes
import base64
import json
import uuid
import re
import requests
import time
import traceback
import logger
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay):
    url_request_list = config_handler.read("urls.cfg", "mercari_jp", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        raw_url_params = re.findall("\?.*", request_url)
        url_params = ""
        if len(raw_url_params) > 0:
            url_params = raw_url_params[0]
        else:
            continue

        rand_uuid = generate_uuid()
        headers = {'DPOP': generate_DPOP(rand_uuid), 'X-Platform': 'web', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0'}

        data = {
            "userId": headers["User-Agent"] + "_" + rand_uuid,
            "pageSize": 120,
            "pageToken": "v1:1",
            "searchSessionId": headers["User-Agent"] + "_" + rand_uuid,
            "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
            "searchCondition": {"status": ["STATUS_DEFAULT"]},
            "defaultDatasets": ["DATASET_TYPE_MERCARI", "DATASET_TYPE_BEYOND"]
            }

        raw_url_params = re.findall("(?<=\?).*", request_url)
        if len(raw_url_params) > 0:
            for raw_url_param in raw_url_params[0].split("&"):
                raw_url_param_eq_split = raw_url_param.split("=")

                if raw_url_param_eq_split[0] == "keyword":
                    data["searchCondition"]["keyword"] = raw_url_param_eq_split[1]
                elif raw_url_param_eq_split[0] == "sort":
                    sorts = {"default": "SORT_DEFAULT", "created_time": "SORT_CREATED_TIME", "num_likes": "SORT_NUM_LIKES", "score": "SORT_SCORE", "price": "SORT_PRICE"}
                    data["searchCondition"]["sort"] = sorts[raw_url_param_eq_split[1]]
                elif raw_url_param_eq_split[0] == "order":
                    orders = {"desc": "ORDER_DESC", "asc": "ORDER_ASC"}
                    data["searchCondition"]["order"] = orders[raw_url_param_eq_split[1]]
                elif raw_url_param_eq_split[0] == "status":
                    statuses = {"default": "STATUS_DEFAULT", "on_sale": "STATUS_ON_SALE", "sold_out": "STATUS_SOLD_OUT"}
                    data["searchCondition"]["status"] = [statuses[raw_url_param_eq_split[1]]]

            data["searchCondition"]["excludeKeyword"] = ""
        else:
            continue

        request_url = request_url.split("?")[0]

        try:
            page = requests.post("https://api.mercari.jp/v2/entities:search", headers=headers, data=json.dumps(data))
        except Exception:
            logger.error_log("Mercari JP request failed. Request url: " + str(request_url) + ", Request headers: " + str(headers), traceback.format_exc())
            continue

        try:
            json_listings = json.loads(page.text)["items"]
        except Exception:
            logger.error_log("Mercari JP json invalid: " + page.text + ", Status code: " + str(page.status_code) + ", Headers: " + str(page.headers), traceback.format_exc())
            continue

        for listing in json_listings:
            item_info = {}
            url = "https://jp.mercari.com/item/" + try_json("id", json_file=listing)
            thumbnail = try_json("thumbnails", 0, json_file=listing)
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
        return str(current_json)
    except Exception:
        logger.error_log("Mercari JP json keys invalid: " + ", json file: " + str(json_file), traceback.format_exc())
        return ""

#taken from https://github.com/marvinody/mercari/blob/master/mercari/DpopUtils.py with minor modifications
def intToBytes(n):
  return n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')

def intToBase64URL(n):
    return bytesToBase64URL(intToBytes(n))

def strToBase64URL(s):
    sBytes = bytes(s, 'utf-8')
    return bytesToBase64URL(sBytes)

def bytesToBase64URL(b):
    return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

def public_key_to_JWK(public_key):
    public_numbers = public_key.public_numbers()
    x,y = (public_numbers.x, public_numbers.y)
    return {"crv": "P-256", "kty": "EC", "x": intToBase64URL(x), "y": intToBase64URL(y)}

def public_key_to_Header(public_key):
    return {"typ": "dpop+jwt", "alg": "ES256", "jwk": public_key_to_JWK(public_key)}

def generate_uuid():
    return str(uuid.uuid4())

def generate_DPOP(dpop_uuid):
    #mercari specific settings
    method = "POST"
    url = "https://api.mercari.jp/v2/entities:search"

    private_key = cryptography.hazmat.primitives.asymmetric.ec.generate_private_key(cryptography.hazmat.primitives.asymmetric.ec.SECP256R1())

    payload = {"iat": int(time.time()), "jti": dpop_uuid, "htu": url, "htm": method.upper()}

    public_key = private_key.public_key()

    header = public_key_to_Header(public_key)

    headerString = json.dumps(header)
    payloadString = json.dumps(payload)

    dataToSign = f"{strToBase64URL(headerString)}.{strToBase64URL(payloadString)}"

    signature = private_key.sign(bytes(dataToSign, 'utf-8'), cryptography.hazmat.primitives.asymmetric.ec.ECDSA(cryptography.hazmat.primitives.hashes.SHA256()))

    r, s = cryptography.hazmat.primitives.asymmetric.utils.decode_dss_signature(signature)
    rB, sB = intToBytes(r), intToBytes(s)

    signatureString = bytesToBase64URL(rB + sB)

    return f"{dataToSign}.{signatureString}"
