import cryptography.hazmat.primitives.asymmetric.ec, cryptography.hazmat.primitives.asymmetric.utils, cryptography.hazmat.primitives.hashes
import base64
import json
import uuid
import re
import requests
import time
import error_logger

def page_parser(request_delay):
    url_request_list = []
    with open("mercari_jp_url_list.txt", "r") as url_request_list_raw:
        url_request_list_lines = url_request_list_raw.readlines()
        url_request_list = list(map(str.strip, url_request_list_lines))

    item_info_list = []
    for request_url in url_request_list:
        raw_url_params = re.findall("\?.*", request_url)
        url_params = ""
        if len(raw_url_params) > 0:
            url_params = raw_url_params[0]
        else:
            continue

        headers = {'DPOP': generate_DPOP(), 'X-Platform': 'web'}
        try:
            page = requests.get("https://api.mercari.jp/search_index/search" + url_params, headers=headers)
        except Exception as e:
            error_logger.error_log("Mercari JP request failed", e)
            continue

        json_listings = json.loads(page.text)
        for listing in json_listings["data"]:
            item_info = {}
            url = "https://jp.mercari.com/item/" + listing["id"]
            thumbnail = listing["thumbnails"][0]
            title = listing["name"]
            price = listing["price"]

            item_info["url"] = url
            item_info["thumbnail"] = thumbnail
            item_info["title"] = title
            item_info["price"] = price

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

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

def generate_DPOP():
    #mercari specific settings
    rand_uuid = str(uuid.uuid4())
    method = "GET"
    url = "https://api.mercari.jp/search_index/search"

    private_key = cryptography.hazmat.primitives.asymmetric.ec.generate_private_key(cryptography.hazmat.primitives.asymmetric.ec.SECP256R1())

    payload = {"iat": int(time.time()), "jti": rand_uuid, "htu": url, "htm": method.upper()}

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
