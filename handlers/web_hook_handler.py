import requests


def set_webhook(TOKEN, ngrok):
    webhook_url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={ngrok}'
    response = requests.post(webhook_url)
    if response.status_code == 200:
        print('Webhook setup successful')
    else:
        print('Webhook setup failed')
