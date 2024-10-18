import os
import traceback
import uvicorn
import logging
import asyncio
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from postgres.database_adapters import del_users_online
# from postgres.database_adapters import start_scheduler, del_users_online
from src.startup import main
from postgres.pool import DbPool
from handlers.db_handlers import bd_router
from handlers.web_hook_handler import webhook_router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from contextlib import asynccontextmanager

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DbPool.create_pool()
        pool = DbPool.get_pool()
        if not pool:
            log.error("Failed to create database connection pool")
            sys.exit(1)
        yield
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        try:
            await DbPool.close_pool()
        except Exception as e:
            log.error(f"An error occurred while closing the database connection pool: {e}")


app = FastAPI(lifespan=lifespan)
app.include_router(bd_router)
app.include_router(webhook_router)

instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)


# async def run_uvicorn():
#     config = uvicorn.Config("app:app", host="0.0.0.0", port=8888, log_level="info")
#     server = uvicorn.Server(config)
#     await server.serve()
#
#
# async def main():
#     pool = await startup()
#
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(del_users_online, 'interval', seconds=60, args=[pool], misfire_grace_time=10)
#     scheduler.start()
#     log.info("The scheduler has been started in the background")
#
#     await run_uvicorn()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log.error(f"Ошибка при запуске: {e}")
        log.debug(traceback.format_exc())
