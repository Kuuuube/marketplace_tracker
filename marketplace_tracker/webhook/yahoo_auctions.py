from datetime import datetime,timezone

def assemble_webhook(item):
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

    return data

def assemble_embed_field(item):
    assembled_string = ""
    #auction and buy it now
    if item["auction"] != "" and item["buy_now"] != "":
        assembled_string = "現在 " + item["price_red"] + "\n" + "即決 " + item["price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #buy it now only
    elif item["buy_now"] != "" and item["auction"] == "":
        assembled_string = "即決 " + item["price_red"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #auction only
    elif item["buy_now"] == "" and item["auction"] != "":
        assembled_string = "現在 " + item["price_red"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    #unknown, give all potentially relevant params
    else:
        assembled_string = "現在 " + item["price_red"] + "\n" + "即決 " + item["price"] + "\n" + "入札 " + item["bidcount"] + "\n" + "残り " + item["time_remaining"]

    return assembled_string