import requests
import logging
import sys
log = logging.getLogger(__name__)


def set_webhook(TOKEN, ngrok, secret_token: str) -> bool:
    webhook_url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={ngrok}/tg_webhooks&secret_token={secret_token}'
    # TODO: need to use try except and print log and exit in case of error
    # TODO: do the same for other checks - checking API key and bot token
    response = requests.post(webhook_url)
    if response.status_code == 200:
        log.info('Webhook setup successful')
    else:
        log.error('Webhook setup failed')
        sys.exit(1)
