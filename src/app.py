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

@app.post("/")
async def tg_webhooks(request: Request):
    if request.method == 'POST':
        async with aiohttp.ClientSession():
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
    loger = logging_config()

    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    TOKEN = os.environ['TOKEN']

    check_bot_token(TOKEN)
    API_KEY = os.environ['API_KEY']
    check_api_key(API_KEY)
    set_webhook(TOKEN, os.environ['APP_DOMAIN'])
    loop = asyncio.get_event_loop()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
