import requests


def set_webhook(TOKEN, ngrok):
    # TODO: need to set secret_token configured via env variable to be able to authorize requests
    #  incoming to web hook requests
    webhook_url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={ngrok}'
    response = requests.post(webhook_url)
    if response.status_code == 200:
        # TODO: need to use logger instead of print
        print('Webhook setup successful')
    else:
        print('Webhook setup failed')
