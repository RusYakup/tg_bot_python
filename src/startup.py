import asyncio
import uvicorn
from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.set_webhook import set_webhook
from postgres.database_adapters import create_table
import logging
from config.config import get_settings
import traceback
from postgres.pool import DbPool
from prometheus.couters import inc_counters

log = logging.getLogger(__name__)


async def startup():
    """
    Perform startup tasks:

    1. Load settings using `get_settings()`.
    2. Configure logging with `logging_config`.
    3. Validate the bot token using `check_bot_token`.
    4. Validate the API key using `check_api_key`.
    5. Set up the webhook for the Telegram bot using `set_webhook`.
    6. Create necessary database tables using `asyncio.run(create_table())`.
    7. Increment counters
    8. Start the scheduler to delete users online every 60 seconds using `AsyncIOScheduler`.
    9. Start the FastAPI application using `uvicorn.Server.serve()`.

    If any of the steps fail, exit with code 1.
    """
    try:
        settings = get_settings()
        logging_config(settings.LOG_LEVEL)
        await DbPool.create_pool()
        pool = await DbPool.get_pool()
        check_bot_token(settings.TOKEN)
        check_api_key(settings.API_KEY)
        set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
        await asyncio.gather(create_table(pool))
        await inc_counters()
        config = uvicorn.Config("src.app:app", host="0.0.0.0", port=8888, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        log.info("Startup completed successfully")
    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n", traceback.format_exc())
        exit(1)
