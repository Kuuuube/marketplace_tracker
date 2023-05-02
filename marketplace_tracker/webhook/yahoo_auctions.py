import time
import requests
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
                        "url": item["thumbnail"]
                    },
                    "footer": {
                        "text": "Yahoo Auctions · " + utc_time
                    }
                }
            ]
        }

        requests.post(url=url, json=data)

        time.sleep(webhook_send_delay)

def assemble_embed_field(item):
    assembled_string = ""
    #auction and buy it now
    if item["buy_now_price"] != "" and item["price"] != "":
        assembled_string = "現在 " + item["price"] + "\n" + "即決 " + item["buy_now_price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #buy it now only
    elif item["buy_now_price"] != "" and item["price"] == "":
        assembled_string = "即決 " + item["buy_now_price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #auction only
    elif item["buy_now_price"] == "" and item["price"] != "":
        assembled_string = "現在 " + item["price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #unknown, give all potentially relevant params
    else:
        assembled_string = "現在 " + item["price"] + "\n" + "即決 " + item["buy_now_price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    return assembled_string