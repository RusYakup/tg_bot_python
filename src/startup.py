from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.set_webhook import set_webhook
from postgres.database_adapters import create_table
import logging
from config.config import get_settings
import traceback
from postgres.pool import DbPool



log = logging.getLogger(__name__)


async def startup():
    try:
        settings = get_settings()
        logging_config(settings.LOG_LEVEL)

        await DbPool.create_pool()
        pool = await DbPool.get_pool()

        check_bot_token(settings.TOKEN)
        check_api_key(settings.API_KEY)
        set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
        await (create_table(pool))

    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n", traceback.format_exc())
        exit(1)
