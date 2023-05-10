# Marketplace Tracker

Tracks new listings on online marketplaces and posts to webhooks.

## Currently supported sites:

- Blocket
- eBay
- Mercari JP
- Mercari US
- Rakuma
- Tradera
- Yahoo Auctions

## Setup

- Add your webhook url to `discord_webhook_url` in `config.cfg`.

- Add the marketplace urls to track to `urls.cfg` under their respective sites. Make sure you have selected all parameters you would like to use on the site's search before copying the url.

- Run `marketplace_tracker.py`

## Config

- `request_send_delay`: The time to wait between requesting marketplace urls.

- `batch_delay`: The time to wait before looping after all marketplace urls have been processed.

- `discord_webhook_url`: The webhook url to send marketplace listings to.

- `webhook_send_delay`: The time to wait between posting to the webhook url.

## Troubleshooting

- To reset all stock tracking, replace the contents of `listings.json` with `{}`.

- If your `config.cfg` or `urls.cfg` become unreadable or throw errors, default versions of `config.cfg` and `urls.cfg` are available in the repo. Replace yours with the defaults and try setting it up again.

- All handled errors are logged to `error_log.txt`. Data from webhook posts that return an unaccepted response are logged to `unsent_webhooks.txt`. If you come across unhandled errors or missing acceptable responses please report them.

- For further support, join the [Discord Server](https://discord.gg/T5vEAh4ruF) or create an issue on this repo.