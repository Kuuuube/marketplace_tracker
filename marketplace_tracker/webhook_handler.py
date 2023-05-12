import requests
import error_logger
import json
import time

accepted_status_codes = [200, 204]

def send_webhook(url, data, webhook_send_delay):
    webhook_request = requests.post(url=url, json=data)

    if webhook_request.status_code in accepted_status_codes:
        resend_unsent(url, webhook_send_delay)
        return True

    else:
        error_logger.error_log("Webhook response bad status code: " + str(webhook_request.status_code) + ", Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(data), "")
        log_unsent(data)
        return False

def log_unsent(data):
    with open("unsent_webhooks.txt", "a", encoding="utf8") as unsent_webhooks_file:
        unsent_webhooks_file.write(json.dumps(data) + "\n")

def resend_unsent(url, webhook_send_delay):
    unsent_webhooks_json_list = []
    try:
        with open("unsent_webhooks.txt", "r", encoding="utf8") as unsent_webhooks_file:
            unsent_webhooks_file_lines = list(map(str.strip, unsent_webhooks_file.readlines()))
            for line in unsent_webhooks_file_lines:
                try:
                    if line == "":
                        continue
                    unsent_webhooks_json_list.append(json.loads(line))
                except Exception as e:
                    error_logger.error_log("Resend Unsent: unsent_webhooks.txt bad line found. Line: " + str(line), e)
    except Exception:
        return #if unsent_webhooks.txt does not exist there are no unsent webhooks

    for unsent_webhooks_json in unsent_webhooks_json_list.copy():
        time.sleep(webhook_send_delay)

        webhook_request = requests.post(url=url, json=unsent_webhooks_json)

        if webhook_request.status_code in accepted_status_codes:
            unsent_webhooks_json_list.remove(unsent_webhooks_json)
        else:
            error_logger.error_log("Resend unsent webhook response bad status code: " + str(webhook_request.status_code) + ", Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(unsent_webhooks_json), "")
            break

        time.sleep(webhook_send_delay)

    with open("unsent_webhooks.txt", "w", encoding="utf8") as unsent_webhooks_file:
        for unsent_webhooks_json in unsent_webhooks_json_list:
            unsent_webhooks_file.write(json.dumps(unsent_webhooks_json) + "\n")
