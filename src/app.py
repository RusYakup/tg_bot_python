from fastapi import FastAPI, Request, HTTPException
from helpers.helpers import check_bot_token, check_api_key
from helpers.check_values import check_chat_id, check_waiting, handlers
from handlers.web_hook_handler import set_webhook
from bot.actions import *
import asyncio
import aiohttp
import json
import requests
from helpers.model_message import *
import os
from telebot.async_telebot import AsyncTeleBot
from waiting.status_of_values import user_input


# TODO: Should call function that configure logger here. That should initiate logger for main module
# logger = logging.getLogger(__name__)
# TODO: In the head of each module should create logger instance with name of the module

app = FastAPI()
bot = AsyncTeleBot(TOKEN)


# @app.post("/")
# async def tg_webhooks(request: Request):
#     webhook_data = await request.json()
#     if request.method == 'POST':
#         json_string = await request.body()
#         json_dict = json.loads(json_string.decode())
#         json_dict['message']['from_user'] = json_dict['message'].pop('from')
#         print(json_dict)

# TODO: should move this handler to the handlers folder. Should use specific path for handling of webhooks,
#  for instance, /tg_webhooks.
@app.post("/")
async def tg_webhooks(request: Request):
    #  TODO: this handler must authorize incoming requests from Telegram via checking of X-Telegram-Bot-Api-Secret-Token header. Read telegram docs
    if request.method == 'POST':
        # TODO: why do you use aiohttp client context manager here?
        async with aiohttp.ClientSession():
            # TODO: should use try except block to catch errors to avoid unexpected crashing
            json_string = await request.body()
            json_dict = json.loads(json_string.decode())
            print(json_dict)
            json_dict['message']['from_user'] = json_dict['message'].pop('from')
            print(user_input)
            try:
                message = Message(**json_dict['message'])
                await check_chat_id(message)

                user_input_values = user_input.get(message.chat.id, {}).values()
                if any(value == 'waiting value' for value in user_input_values):
                    await check_waiting(message)
                else:
                    await handlers(bot, message)
            except ValidationError:
                print(json_dict['message'])


if __name__ == "__main__":
    # TODO: We are not needed to store logger to variable because you dont' use it
    loger = logging_config()

    # TODO: should declare all imports in the head of the module if it's not specific case
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    # TODO: what happen if there is no TOKEN env variable? The same for other env variables
    # TODO: should check that mandatory env variables are configured. IN other case, print error log and exit the app with error code
    TOKEN = os.environ['TOKEN']
    # TODO: should exit app in the case when checking of bot token and api key and configuring of the webhook url are failed
    # TODO: what happen if exception occur in function that you call?
    check_bot_token(TOKEN)
    API_KEY = os.environ['API_KEY']
    check_api_key(API_KEY)
    set_webhook(TOKEN, os.environ['APP_DOMAIN'])
    loop = asyncio.get_event_loop()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
