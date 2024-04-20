import requests
from dotenv import load_dotenv
import os
import time


load_dotenv()

TOKEN = os.getenv('TOKEN')
ngrok = os.getenv('NGROK_DOMAIN')

# url = f'{webhook_url}/bot{TOKEN}'

webhook_url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={ngrok}'

response = requests.post(webhook_url)
if response.status_code == 200:
    print('Webhook setup successful')
else:
    print('Webhook setup failed')

