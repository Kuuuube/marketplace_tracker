import json
import logger
import os
import sys

def read_json_dict(json_file):
    with open (json_file, "r") as items:
        return(json.load(items))

def rewrite_json_dict(json_file, current_json, list, differentiating_key, retries = 5):
    current_retry = 0
    while current_retry < retries:
        #write temp file first
        with open (json_file + ".tmp", "w", encoding = "utf8") as states:
            for item in list:
                current_json[item[differentiating_key]] = "Found"
            json.dump(current_json, states)

        #remove previous backup only if temp file was written correctly
        if os.path.exists(json_file + ".bak"):
            if validate_json(json_file + ".tmp", current_json):
                os.remove(json_file + ".bak")
                break
            else:
                if current_retry >= retries:
                    logger.error_log("Invalid temp file written: " + str(json_file) + ".tmp, Unrecoverable state detected. Stopping.", "")
                    sys.exit()
                else:
                    logger.error_log("Invalid temp file written: " + str(json_file) + ".tmp, Retrying " + str(retries) + " times, current retry: " + str(current_retry), "")
                current_retry += 1
        else:
            break

    #rename existing json
    if os.path.exists(json_file):
        os.rename(json_file, json_file + ".bak")

    #rename temp file to be new original file
    os.rename(json_file + ".tmp", json_file)

def validate_json(json_file, expected_data = ""):
    try:
        with open(json_file) as validate_file:
            #only json validation
            if expected_data == "":
                json.load(validate_file)
                return True

            #json and data validation
            if json.load(validate_file) == expected_data:
                return True
            else:
                return False
    except Exception as e:
        logger.error_log("Failed to validate json file: " + str(json_file), e)
        return False