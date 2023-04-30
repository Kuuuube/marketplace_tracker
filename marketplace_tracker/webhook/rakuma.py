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
                        "url": item["thumbnail"]
                    },
                    "footer": {
                        "text": "Rakuma · " + utc_time
                    }
                }
            ]
        }

        requests.post(url=url, json=data)

        time.sleep(webhook_send_delay)

def assemble_embed_field(item):
    assembled_string = "¥" + add_commas(item["price"])
    return assembled_string

def add_commas(string):
    try:
        return format(int(string), ",d")
    except Exception:
        pass

    try:
        return format(int(string.split(".")[0]), ",d") + "." + string.split(".")[1]
    except Exception:
        pass

    return string