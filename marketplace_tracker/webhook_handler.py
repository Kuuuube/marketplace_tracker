import requests
import error_logger

def send_webhook(url, data):
    webhook_request = requests.post(url=url, json=data)

    if webhook_request.status_code == 200:
        return True

    if webhook_request.status_code != 200:
        error_logger.error_log("Webhook request bad status code: " + str(webhook_request.status_code) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(data), "")
        return False