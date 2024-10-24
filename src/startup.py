import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.set_webhook import set_webhook
from postgres.database_adapters import create_table, del_users_online
import logging
from config.config import get_settings
import traceback
from postgres.pool import DbPool
from prometheus.couters import inc_counters

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
        await create_table(pool)
        await inc_counters()

        log.info("Startup completed successfully")
        return pool
    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n", traceback.format_exc())
        exit(1)


async def run_uvicorn():
    config = uvicorn.Config("src.app:app", host="0.0.0.0", port=8888, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    pool = await startup()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(del_users_online, 'interval', seconds=60, args=[pool], misfire_grace_time=10)
    scheduler.start()
    log.info("The scheduler has been started in the background")

    await run_uvicorn()
