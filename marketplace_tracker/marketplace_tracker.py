import time
import json_handler
import config_handler
import parser.ebay, parser.yahoo_auctions, parser.rakuma, parser.mercari_jp
import webhook.ebay, webhook.yahoo_auctions, webhook.rakuma, webhook.mercari_jp

discord_webhook_url = config_handler.read("config.cfg", "webhook", "discord_webhook_url")

webhook_send_delay = int(config_handler.read("config.cfg", "webhook", "webhook_send_delay"))
request_delay = int(config_handler.read("config.cfg", "requests", "request_send_delay"))
batch_delay = int(config_handler.read("config.cfg", "requests", "batch_delay"))

json_file = "listings.json"

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

while True:
    listing_check(parser.ebay.page_parser, webhook.ebay.send_webhook, "url")
    listing_check(parser.yahoo_auctions.page_parser, webhook.yahoo_auctions.send_webhook, "url")
    listing_check(parser.rakuma.page_parser, webhook.rakuma.send_webhook, "url")
    listing_check(parser.mercari_jp.page_parser, webhook.mercari_jp.send_webhook, "url")

    print("Batch complete, waiting: " + str(batch_delay) + " seconds")
    time.sleep(batch_delay)