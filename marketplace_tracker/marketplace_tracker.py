import importlib
import os
import time
import json
import traceback
import logger
from datetime import datetime,timezone
import json_handler
import config_handler
import webhook_handler

discord_webhook_url = config_handler.read("config.cfg", "webhook", "discord_webhook_url")
uptime_webhook_url = config_handler.read("config.cfg", "webhook", "uptime_webhook_url")

webhook_send_delay = int(config_handler.read("config.cfg", "webhook", "webhook_send_delay"))
request_delay = int(config_handler.read("config.cfg", "requests", "request_send_delay"))
batch_delay = int(config_handler.read("config.cfg", "requests", "batch_delay"))

request_timeout = 60

json_file = "listings.json"

marketplace_modules = {}

def import_folders(*folders, modules_dict):
    for folder in folders:
        for module_file in os.listdir(os.path.dirname(__file__) + "/" + folder):
            if module_file.endswith(".py"):
                module_name = module_file.replace(".py", "")
                if module_name not in modules_dict.keys():
                    modules_dict[module_name] = {}
                modules_dict[module_name][folder] = importlib.import_module(folder + "." + module_name)

def listing_check(parser_func, webhook_func, differentiating_key):
    new_listings_list = parser_func(request_delay, request_timeout)

    if len(new_listings_list) < 1:
        return

    listings_dict = json_handler.read_json_dict(json_file)
    new_items = []
    for item in new_listings_list:
        if item[differentiating_key] not in listings_dict:
            new_items.append(item)

    new_listings_bak_file = "new_listings.bak"
    #new listings should be recoverable if there is a crash while sending webhooks
    with open(new_listings_bak_file, "w", encoding = "utf8") as new_listings_bak:
        for item in new_items:
            new_listings_bak.write(json.dumps(item) + "\n")

    json_handler.rewrite_json_dict(json_file, listings_dict, new_items, differentiating_key, 5)

    for item in new_items:
        webhook_data = webhook_func(item)
        webhook_handler.send_webhook(discord_webhook_url, webhook_data, webhook_send_delay, request_timeout)

        time.sleep(webhook_send_delay)

    #after webhooks are sent the new_listings.bak is no longer needed
    os.remove(new_listings_bak_file)

#imports parser and webhook folders to marketplace_modules dict
import_folders("parser", "webhook", modules_dict=marketplace_modules)

#send bot started notification to uptime webhook
utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
webhook_handler.send_unhandled_webhook(uptime_webhook_url, request_timeout, data = {"content": "","embeds": [{"title": "Bot started","description": utc_time}]})

while True:
    try:
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        logger.log(utc_time + " Batch started")
        for marketplace_module in marketplace_modules.values():
            if "parser" not in marketplace_module.keys() or "webhook" not in marketplace_module.keys():
                continue

            listing_check(marketplace_module["parser"].page_parser, marketplace_module["webhook"].assemble_webhook, marketplace_module["parser"].get_differentiating_key())

        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

        logger.log(utc_time + " Batch complete, waiting: " + str(batch_delay) + " seconds")
        webhook_handler.send_unhandled_webhook(uptime_webhook_url, request_timeout, data = {"content": "","embeds": [{"title": "Batch complete","description": utc_time}]})

        time.sleep(batch_delay)
    except Exception:
        try:
            logger.error_log("Crash in main process, attempting to recover in " + str(batch_delay) + " seconds", traceback.format_exc())
            webhook_handler.send_unhandled_webhook(uptime_webhook_url, request_timeout, data = {"content": "","embeds": [{"title": "Crash in main process","description": "Attempting to recover in " + str(batch_delay) + " seconds\n```\n" + str(traceback.format_exc())[:2048] + "\n```"}]})
            time.sleep(batch_delay)
        except Exception:
            time.sleep(batch_delay)
