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
                    "text": "Mercari US · " + utc_time
                }
            }
        ]
    }

    return data
def assemble_embed_field(item):
    assembled_string = "$" + remove_last_two_digits(item["price"])
    return assembled_string

def remove_last_two_digits(string):
    try:
        return format(float(string) / 100, ",.0f")
    except Exception:
        pass

    return string