import requests
import logging
import sys
import traceback
from telebot.async_telebot import AsyncTeleBot
from asyncpg.pool import Pool
from helpers.config import get_settings, Settings, get_bot
import json
from helpers.model_message import Message
from postgres.database_adapters import create_pool
from helpers.check_values import check_chat_id, check_waiting, handlers
from pydantic import ValidationError
from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from postgres.database_adapters import verify_credentials
from fastapi.security import HTTPBasicCredentials
from postgres.database_adapters import execute

log = logging.getLogger(__name__)
app = FastAPI()


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


# TODO: move to the webhook handler module

@app.post("/tg_webhooks")
async def tg_webhooks(request: Request, config: Annotated[Settings, Depends(get_settings)],
                      bot: AsyncTeleBot = Depends(get_bot), pool: Pool = Depends(create_pool)):
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
                log.error("Exception traceback", traceback.format_exc())
                return bot.send_message(message.chat.id, "An error occurred, please try again later")
        else:
            log.error(f"Invalid request method: {request.method}")
            return HTTPException(status_code=405, detail="Method not allowed")
    else:
        log.error(f"Invalid X-Telegram-Bot-Api-Secret-Token: {x_telegram_bot_api_secret_token}")
        return HTTPException(status_code=401, detail="Unauthorized")


@app.get("/users_actions")
async def get_users_actions(chat_id: int,
                            from_ts: int = None,
                            until_ts: int = None,
                            limit: int = 1000,
                            credentials: HTTPBasicCredentials = Security(verify_credentials),
                            pool: Pool = Depends(create_pool)):
    """
      Retrieves user actions based on the provided criteria.
      Args:
          chat_id (int): The ID of the chat/user.
          from_ts (int, optional): The starting timestamp. Defaults to None.
          until_ts (int, optional): The ending timestamp. Defaults to None.
          limit (int, optional): The maximum number of results to retrieve. Defaults to 1000.
          credentials (HTTPBasicCredentials, optional): Security credentials. Defaults to Security(verify_credentials).
          pool (Pool, optional): The global database connection pool. Defaults to Depends(create_pool).
      Returns:
          list: The list of user actions retrieved based on the criteria.
      Raises:
          HTTPException: If there is an unauthorized access or an error occurs during retrieval.
      """
    try:
        if from_ts is not None and until_ts is not None:
            print("SELECT * FROM statistic WHERE chat_id = $1 AND ts >= $2 AND ts <= $3 ORDER BY ts DESC LIMIT $4")
            query = "SELECT * FROM statistic WHERE chat_id = $1 AND ts >= $2 AND ts <= $3 ORDER BY ts DESC LIMIT $4"
            args = [chat_id, from_ts, until_ts, limit]
            res = await execute(pool, query, *args, fetch=True)
        if from_ts is not None:
            print("SELECT * FROM statistic WHERE chat_id = $1 AND ts >= $2 ORDER BY ts DESC LIMIT $3")
            query = "SELECT * FROM statistic WHERE chat_id = $1 AND ts >= $2 ORDER BY ts DESC LIMIT $3"
            args = [chat_id, from_ts, limit]
            res = await execute(pool, query, *args, fetch=True)
        else:
            print("SELECT * FROM statistic WHERE chat_id = $1")
            query = "SELECT * FROM statistic WHERE chat_id = $1"
            args = [chat_id]
            res = await execute(pool, query, *args, fetch=True)
        return res
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback", traceback.format_exc())


@app.get("/actions_count")
async def get_actions_count(chat_id: int,
                            from_ts: int = None,
                            until_ts: int = None,
                            credentials: HTTPBasicCredentials = Security(verify_credentials),
                            pool: Pool = Depends(create_pool)):
    """
     Retrieves the count of actions based on the provided chat_id.

     Args:
         chat_id (int): The ID of the chat/user.
         from_ts (int, optional): The starting timestamp. Defaults to None.
         until_ts (int, optional): The ending timestamp. Defaults to None.
         credentials (HTTPBasicCredentials, optional): Security credentials. Defaults to Security(verify_credentials).
         pool (Pool, optional): The global database connection pool. Defaults to Depends(create_pool).

     Returns:
         dict: The count of actions based on the provided chat_id.

     Raises:
         HTTPException: If there is an unauthorized access or an error occurs during retrieval.
     """
    query = "SELECT chat_id, DATE_TRUNC('month', to_timestamp(ts)) AS month, COUNT(*) AS actions_count FROM statistic WHERE chat_id = $1 GROUP BY chat_id, month"
    args = [chat_id]
    res = await execute(pool, query, *args, fetch=True)
    return res
