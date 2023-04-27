import time
import webhook_handler
import json_handler
import page_parser
import config_handler

discord_webhook_url = config_handler.read("config.cfg", "webhook", "discord_webhook_url")
webhook_send_delay = int(config_handler.read("config.cfg", "webhook", "webhook_send_delay"))

request_delay = int(config_handler.read("config.cfg", "requests", "request_send_delay"))
batch_delay = int(config_handler.read("config.cfg", "requests", "batch_delay"))

json_file = "listings.json"

def ebay_handler():
    ebay_url_list = page_parser.ebay_page_parser(request_delay)

    new_items = []

    for item in ebay_url_list:
        listings_dict = json_handler.read_json_dict(json_file)
        if item["url"] not in listings_dict:
            new_items.append(item)

    json_handler.rewrite_json_dict(json_file, listings_dict, new_items)

    webhook_handler.send_webhook(discord_webhook_url, new_items, webhook_send_delay)

while True:
    ebay_handler()

    print("Batch complete, waiting: " + str(batch_delay) + " seconds")
    time.sleep(batch_delay)