from fastapi import FastAPI, Request, HTTPException, Header
from helpers.helpers import check_bot_token, check_api_key, check_env_variables, logging_config
from helpers.check_values import check_chat_id, check_waiting, handlers
from handlers.web_hook_handler import set_webhook
from bot.actions import *
import uvicorn
import asyncio
import aiohttp
import json
import requests
from helpers.model_message import *
import os
from telebot.async_telebot import AsyncTeleBot
from waiting.status_of_values import user_input
from dotenv import load_dotenv, find_dotenv
import logging
from helpers.model_setting_env import Settings


app = FastAPI()
bot = AsyncTeleBot(TOKEN)
log = logging.getLogger(__name__)


@app.post("/tg_webhooks")
async def tg_webhooks(request: Request):
    x_telegram_bot_api_secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if request.method == 'POST':
        # TODO: why do you use aiohttp client context manager here?
        async with aiohttp.ClientSession():
            try:
                if x_telegram_bot_api_secret_token == settings.SECRET_TOKEN_TG_WEBHOOK:
                    json_string = await request.body()
                    json_dict = json.loads(json_string.decode())
                    json_dict['message']['from_user'] = json_dict['message'].pop('from')
                    message = Message(**json_dict['message'])
                    await check_chat_id(message)

                    user_input_values = user_input.get(message.chat.id, {}).values()
                    if any(value == 'waiting value' for value in user_input_values):
                        await check_waiting(message)
                    else:
                        await handlers(bot, message)
                else:
                    raise HTTPException(status_code=401, detail="Unauthorized")
            except ValidationError:
                log.error("ValidationError: %s", json_dict)
            except Exception as e:
                log.error("An error occurred: %s", str(e))
                log.error(traceback.format_exc())
                await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')




if __name__ == "__main__":
    settings = Settings()
    TOKEN, API_KEY, APP_DOMAIN, TG_BOT_API_URL, SECRET_TOKEN_TG_WEBHOOK, LOG_LEVEL = settings.TOKEN, settings.API_KEY, settings.APP_DOMAIN, settings.TG_BOT_API_URL, settings.SECRET_TOKEN_TG_WEBHOOK, settings.LOG_LEVEL
    load_dotenv(find_dotenv())
    logging_config(LOG_LEVEL)
    env_vars = ['TOKEN', 'API_KEY', 'APP_DOMAIN', 'TG_BOT_API_URL', 'SECRET_TOKEN_TG_WEBHOOK', 'LOG_LEVEL']
    check_env_variables(env_vars)
    check_bot_token(TOKEN)
    check_api_key(API_KEY)
    set_webhook(TOKEN, APP_DOMAIN, SECRET_TOKEN_TG_WEBHOOK)
    loop = asyncio.get_event_loop()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
