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
                    "text": "Mercari JP · " + utc_time
                }
            }
        ]
    }

    return data

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