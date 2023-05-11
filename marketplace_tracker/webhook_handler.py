import requests
import error_logger

def send_webhook(url, data):
    webhook_request = requests.post(url=url, json=data)

    accepted_status_codes = [200, 204]

    if webhook_request.status_code in accepted_status_codes:
        return True

    else:
        error_logger.error_log("Webhook response bad status code: " + str(webhook_request.status_code) + "Response headers: " + str(webhook_request.headers) + ", Request response: " + str(webhook_request.text) + ", Webhook data: " + str(data), "")
        return False
