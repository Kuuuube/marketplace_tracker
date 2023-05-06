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
                    "text": "Blocket · " + utc_time
                }
            }
        ]
    }

    return data

def assemble_embed_field(item):
    assembled_string = item["price"]
    return assembled_string