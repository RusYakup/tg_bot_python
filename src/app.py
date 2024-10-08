import traceback
from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.set_webhook import set_webhook
from postgres.database_adapters import create_table
import uvicorn
import asyncio
import logging
from config.config import get_settings
from handlers.web_hook_handler import app
from prometheus_fastapi_instrumentator import Instrumentator


log = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        #Instrumentator().instrument(app).expose(app)
        settings = get_settings()
        logging_config(settings.LOG_LEVEL)
        check_bot_token(settings.TOKEN)
        check_api_key(settings.API_KEY)
        set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
        asyncio.run(create_table())
        uvicorn.run(app, host="0.0.0.0", port=8888)
    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n", traceback.format_exc())
        exit(1)
