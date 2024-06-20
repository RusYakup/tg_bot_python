import requests
import logging
import sys
import traceback

log = logging.getLogger(__name__)


def set_webhook(token: str, ngrok: str, secret_token: str) -> None:
    """
    Sets up a webhook for the Telegram bot using the provided tokens.
    Parameters:
        token (str): The Telegram bot token.
        ngrok (str): The ngrok URL.
        secret_token (str): The secret token for the webhook.
    Raises:
        SystemExit: If the webhook setup fails.
    Returns:
        None
    """
    try:
        webhook_url = f'https://api.telegram.org/bot{token}/setWebhook?url={ngrok}/tg_webhooks&secret_token={secret_token}'
        # TODO: here can be exception -> need to catch it
        response = requests.post(webhook_url)
        if response.status_code == 200:
            log.info('Webhook setup successful')
            return
        else:
            log.error('Webhook setup failed')
            sys.exit(1)
    except Exception as e:
        log.error(f'Webhook setup failed :\n{e}')
        log.debug(F"Exception traceback:\n", traceback.format_exc())
        sys.exit(1)


