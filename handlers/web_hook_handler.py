import logging
import traceback
from telebot.async_telebot import AsyncTeleBot
from asyncpg.pool import Pool
from config.config import get_settings, Settings, get_bot
import json
from helpers.model_message import Message
from helpers.check_values import check_chat_id, check_waiting, handlers
from pydantic import ValidationError
from typing import Annotated
from fastapi import Request, HTTPException, Depends, APIRouter
from postgres.pool import get_db_pool



log = logging.getLogger(__name__)


webhook_router = APIRouter()


@webhook_router.post("/tg_webhooks")
async def tg_webhooks(request: Request, config: Annotated[Settings, Depends(get_settings)],
                      bot: AsyncTeleBot = Depends(get_bot), pool: Pool = Depends(get_db_pool)):
    """
    Handle incoming Telegram webhook requests.

    Parameters:
    - request: Request object containing the incoming request data
    - config: Settings configuration
    - bot: AsyncTeleBot instance for interacting with Telegram API
    - pool: Pool object for database connection

    Returns:
    - HTTPException if there are errors in processing the request
    """
    # Get X-Telegram-Bot-Api-Secret-Token from headers
    x_telegram_bot_api_secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')

    # Check if the X-Telegram-Bot-Api-Secret-Token is correct
    if x_telegram_bot_api_secret_token == config.SECRET_TOKEN_TG_WEBHOOK:
        if request.method == 'POST':
            try:
                # Get the JSON data from the request body
                json_string = await request.body()
            except json.decoder.JSONDecodeError:
                log.error("Telegram webhook request body: JSONDecodeError")
                log.debug("Exception traceback", traceback.format_exc())
                return HTTPException(status_code=400,
                                     detail="JSONDecodeError: An error occurred, please try again later")
            try:
                # Decode the JSON data and create a Message object
                json_dict = json.loads(json_string.decode())
                json_dict['message']['from_user'] = json_dict['message'].pop('from')
                message = Message(**json_dict['message'])
            except ValidationError:
                log.error("ValidationError occurred Message")
                log.debug(traceback.format_exc())
                return HTTPException(status_code=400,
                                     detail="ValidationError: An error occurred, please try again later")
            try:
                # Check the chat ID and process the message accordingly
                status_user = await check_chat_id(pool, message)
                print(message)

                # Check if user is waiting for a value to be entered
                if "waiting_value" in status_user.values():
                    await check_waiting(status_user, pool, message, bot, config)
                else:
                    await handlers(pool, message, bot, config, status_user)
            except Exception as exc:
                log.error("An error occurred: %s", str(exc))
                log.debug("Exception traceback", traceback.format_exc())
                return bot.send_message(message.chat.id, "An error occurred, please try again later")
        else:
            log.error(f"Invalid request method: {request.method}")
            return HTTPException(status_code=405, detail="Method not allowed")
    else:
        log.error(f"Invalid X-Telegram-Bot-Api-Secret-Token: {x_telegram_bot_api_secret_token}")
        return HTTPException(status_code=401, detail="Unauthorized")
