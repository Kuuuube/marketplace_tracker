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
                        "text": "Tradera · " + utc_time
                    }
                }
            ]
        }

        requests.post(url=url, json=data)

        time.sleep(webhook_send_delay)

def assemble_embed_field(item):
    assembled_string = ""
    #auction and buy it now
    if item["buy_it_now_label"] != "" and item["bidcount"] != "":
        assembled_string = item["buy_it_now_label"] + " " + item["buy_it_now_price"] + "\n" + item["price"] + " " + item["bidcount"]

    #buy it now only
    elif item["buy_it_now_label"] != "" and item["bidcount"] == "":
        assembled_string = item["buy_it_now_label"] + " " + item["price"]

    #auction only
    elif item["buy_it_now_label"] == "" and item["bidcount"] != "":
        assembled_string = item["price"] + " " + item["bidcount"]

    #unknown, give all potentially relevant params
    else:
        assembled_string = item["buy_it_now_label"] + " " + item["buy_it_now_price"] + "\n" + item["price"] + " " + item["bidcount"]

    return assembled_string