import requests
import logger
import json
import time
import traceback

accepted_status_codes = [200, 204]

def send_webhook(url, data, webhook_send_delay, request_timeout):
    webhook_request = requests.post(url=url, json=data, timeout=request_timeout)

    if webhook_request.status_code in accepted_status_codes:
        resend_unsent(url, webhook_send_delay, request_timeout)
        return True

    else:
        logger.error_log("Webhook response bad status code: " + str(webhook_request.status_code) + ", Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(data), "")
        log_unsent(data)
        return False

def log_unsent(data):
    with open("unsent_webhooks.txt", "a", encoding="utf8") as unsent_webhooks_file:
        unsent_webhooks_file.write(json.dumps(data) + "\n")

def resend_unsent(url, webhook_send_delay, request_timeout):
    unsent_webhooks_json_list = []
    try:
        with open("unsent_webhooks.txt", "r", encoding="utf8") as unsent_webhooks_file:
            unsent_webhooks_file_lines = list(map(str.strip, unsent_webhooks_file.readlines()))
            for line in unsent_webhooks_file_lines:
                try:
                    if line == "":
                        continue
                    unsent_webhooks_json_list.append(json.loads(line))
                except Exception:
                    logger.error_log("Resend Unsent: unsent_webhooks.txt bad line found. Line: " + str(line), traceback.format_exc())
    except Exception:
        return #if unsent_webhooks.txt does not exist there are no unsent webhooks

    for unsent_webhooks_json in unsent_webhooks_json_list.copy():
        time.sleep(webhook_send_delay)

        webhook_request = requests.post(url=url, json=unsent_webhooks_json, timeout=request_timeout)

        if webhook_request.status_code in accepted_status_codes:
            unsent_webhooks_json_list.remove(unsent_webhooks_json)
        else:
            logger.error_log("Resend unsent webhook response bad status code: " + str(webhook_request.status_code) + ", Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(unsent_webhooks_json), "")
            break

        time.sleep(webhook_send_delay)

    with open("unsent_webhooks.txt", "w", encoding="utf8") as unsent_webhooks_file:
        for unsent_webhooks_json in unsent_webhooks_json_list:
            unsent_webhooks_file.write(json.dumps(unsent_webhooks_json) + "\n")

def send_unhandled_webhook(url, request_timeout, data):
    try:
        if url == "":
            return

        webhook_request = requests.post(url=url, json=data, timeout=request_timeout)

        if webhook_request.status_code not in accepted_status_codes:
            logger.error_log("Webhook response bad status code: " + str(webhook_request.status_code) + ", Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(data), "")

    except Exception:
        logger.error_log("Uptime webhook failed", traceback.format_exc())