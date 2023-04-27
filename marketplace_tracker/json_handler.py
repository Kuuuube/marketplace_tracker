import json

def read_json_dict(json_file):
    with open (json_file, "r") as items:
        return(json.load(items))

def rewrite_json_dict(json_file, current_json, list):
    with open (json_file, "w") as states:
        for item in list:
            current_json[item["url"]] = "Found"
        json.dump(current_json, states)