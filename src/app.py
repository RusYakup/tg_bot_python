from fastapi import FastAPI, Request, HTTPException, Depends
from typing import Annotated
from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.check_values import check_chat_id, check_waiting #, handlers,
from handlers.web_hook_handler import set_webhook
#from postgres.func import execute_query #create_table, load_data,
from bot.actions import *
import uvicorn
import asyncio
import json
from helpers.model_message import *
#from helpers.status_of_values import user_input
import logging
from helpers.config import get_settings, Settings, get_bot, DataBase, DataBaseClass # create_pool
from telebot.async_telebot import AsyncTeleBot
import traceback


import asyncpg

app = FastAPI()

log = logging.getLogger(__name__)


# TODO: move to the webhook handler module

@app.post("/tg_webhooks")
async def tg_webhooks(request: Request, config: Annotated[Settings, Depends(get_settings)],
                      bot: AsyncTeleBot = Depends(get_bot)):
    await DataBase.create_pool()
    x_telegram_bot_api_secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if x_telegram_bot_api_secret_token == settings.SECRET_TOKEN_TG_WEBHOOK:
        if request.method == 'POST':
            try:
                json_string = await request.body()
            except json.decoder.JSONDecodeError:
                log.error("Telegram webhook request body: JSONDecodeError")
                log.debug("Exception traceback", traceback.format_exc())
                return HTTPException(status_code=400,
                                     detail="JSONDecodeError: An error occurred, please try again later")
            try:
                json_dict = json.loads(json_string.decode())
                json_dict['message']['from_user'] = json_dict['message'].pop('from')
                message = Message(**json_dict['message'])
            except ValidationError:
                log.error("ValidationError occurred Message")
                log.debug(traceback.format_exc())
                return HTTPException(status_code=400,
                                     detail="ValidationError: An error occurred, please try again later")
            try:
                print(message)
                use = 'user_state'
                res = await DataBase.execute("SELECT * FROM user_state", fetch=True)
                print(res)
                query = ("INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) "
                         "ON CONFLICT (chat_id) DO NOTHING")
                args = [90100, "Я поебдил", "эту", "Хрень"]
                await DataBase.execute(query, *args, fetch=True)
                await check_chat_id(message, DataBase)
                await check_waiting(message, bot, config)
                # await handlers(message, bot, config)

                query =
                # user_input_values = user_input.get(message.chat.id, {}).values()
                # if any(value == 'waiting value' for value in user_input_values):
                #     await check_waiting(message, bot, config)
                # else:
                #     await handlers(message, bot, config)
            except Exception as exc:
                log.error("An error occurred: %s", str(exc))
                log.error("Exception traceback", traceback.format_exc())
                # return bot.send_message(message.chat.id, "An error occurred, please try again later")
        else:
            log.error(f"Invalid request method: {request.method}")
            return HTTPException(status_code=405, detail="Method not allowed")
    else:
        log.error(f"Invalid X-Telegram-Bot-Api-Secret-Token: {x_telegram_bot_api_secret_token}")
        return HTTPException(status_code=401, detail="Unauthorized")


async def mainer(pool):
    try:
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO UPDATE SET city = $2, date_difference = $3, qty_days = $4"
        args = [000, "Moskva", "Nondde", "None"]
        await execute_query(query, *args)
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO UPDATE SET city = $2, date_difference = $3, qty_days = $4"
        args = [0000000000, "Moskva2", "Noddne2", "None2"]
        await execute_query(query, *args)
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO NOTHING"
        args = [1110000311, "Moskva", "Nondde", "None"]
        await execute_query(query, *args)

    except Exception as e:
        log.debug("An error occurred: %s", str(e))
        log.debug(traceback.format_exc())
        exit(1)




if __name__ == "__main__":
    try:
        settings = get_settings()
        logging_config(settings.LOG_LEVEL)
        check_bot_token(settings.TOKEN)
        check_api_key(settings.API_KEY)
        set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(DataBase.create_pool())
        asyncio.run(DataBase.create_table())
        uvicorn.run(app, host="0.0.0.0", port=8888)

    except Exception as e:
        log.error(e)
        log.error(f"Exception traceback:\n", traceback.format_exc())
        exit(1)

# if __name__ == "__main__":
#     try:
#         settings = get_settings()
#     except Exception as e:
#         log.error(e)
#         log.error(f"Exception traceback:\n", traceback.format_exc())
#         exit(1)
#
#     logging_config(settings.LOG_LEVEL)
#     check_bot_token(settings.TOKEN)
#     check_api_key(settings.API_KEY)
#     set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
#     pool = asyncio.run(create_pool())
#     loop = asyncio.get_event_loop()
#     # asyncio.run(create_table(pool=pool))
#
#     uvicorn.run(app, host="0.0.0.0", port=8888)
