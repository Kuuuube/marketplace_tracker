import time
import requests
import re
from datetime import datetime,timezone

def send_webhook(url, new_items, webhook_send_delay):
    for item in new_items:
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "content": "",
            "embeds": [
                {
                    "title": item["title"],
                    "url": item["url"],
                    "fields": [
                        {
                        "name": assemble_embed_field(item),
                        "value": ""
                        }
                    ],
                    "thumbnail": {
                        "url": get_bigger_thumbnail(item["thumbnail"])
                    },
                    "footer": {
                        "text": "eBay · " + utc_time
                    }
                }
            ]
        }

        requests.post(url=url, json=data)

        time.sleep(webhook_send_delay)

def assemble_embed_field(item):
    assembled_string = ""
    #auction and buy it now
    if item["buy_it_now_price"] != "" and item["bidding_price"] != "":
        assembled_string = item["bidding_price"] + "\n" + item["bidcount"] + "\n" + item["buy_it_now_price"] + "\n" + item["purchase_option"] + "\n" + item["shipping"]

    #buy it now only
    elif item["buy_it_now_price"] != "" and item["bidding_price"] == "":
        assembled_string = item["buy_it_now_price"] + "\n" + item["purchase_option"] + "\n" + item["shipping"]

    #auction with or best offer
    elif item["buy_it_now_price"] == "" and item["bidding_price"] != "" and item["purchase_option"] != "":
        assembled_string = item["bidding_price"] + "\n" + item["bidcount"] + "\n" + item["purchase_option"] + "\n" + item["shipping"]

    #auction only
    elif item["buy_it_now_price"] == "" and item["bidding_price"] != "":
        assembled_string = item["bidding_price"] + "\n" + item["bidcount"] + "\n" + item["shipping"]

    #unknown, give all potentially relevant params
    else:
        assembled_string = item["bidding_price"] + "\n" + item["bidcount"] + "\n" + item["buy_it_now_price"] + "\n" + item["purchase_option"] + "\n" + item["shipping"]

    return assembled_string

def get_bigger_thumbnail(small_thumbnail_url):
    return re.sub("s-l225", "s-l500",re.sub("thumbs/", "", small_thumbnail_url))