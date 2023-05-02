import importlib
import os
import time
from datetime import datetime,timezone
import json_handler
import config_handler

discord_webhook_url = config_handler.read("config.cfg", "webhook", "discord_webhook_url")

webhook_send_delay = int(config_handler.read("config.cfg", "webhook", "webhook_send_delay"))
request_delay = int(config_handler.read("config.cfg", "requests", "request_send_delay"))
batch_delay = int(config_handler.read("config.cfg", "requests", "batch_delay"))

json_file = "listings.json"

marketplace_modules = {}

def import_folders(*folders):
    for folder in folders:
        for module_file in os.listdir(os.path.dirname(__file__) + "/" + folder):
            if module_file.endswith(".py"):
                module_name = module_file.replace(".py", "")
                if module_name not in marketplace_modules.keys():
                    marketplace_modules[module_name] = {}
                marketplace_modules[module_name][folder] = importlib.import_module(folder + "." + module_name)

def listing_check(parser_func, webhook_func, differentiating_key):
    url_list = parser_func(request_delay)

    if len(url_list) < 1:
        return

    new_items = []
    for item in url_list:
        listings_dict = json_handler.read_json_dict(json_file)
        if item[differentiating_key] not in listings_dict:
            new_items.append(item)

    json_handler.rewrite_json_dict(json_file, listings_dict, new_items)

    webhook_func(discord_webhook_url, new_items, webhook_send_delay)

#imports everything in the parser and webhook folders
import_folders("parser", "webhook")

while True:
    for marketplace_module in marketplace_modules.values():
        if "parser" not in marketplace_module.keys() or "webhook" not in marketplace_module.keys():
            continue

        listing_check(marketplace_module["parser"].page_parser, marketplace_module["webhook"].send_webhook, "url")

    utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    print(utc_time + " Batch complete, waiting: " + str(batch_delay) + " seconds")
    time.sleep(batch_delay)