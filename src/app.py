import traceback
import uvicorn
import logging
import asyncio
from config.startup import startup
from postgres.pool import DbPool
from handlers.db_handlers import bd_router
from handlers.web_hook_handler import webhook_router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from contextlib import asynccontextmanager


log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DbPool.create_pool()
    try:
        yield
    finally:
        await DbPool.close_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(bd_router)
app.include_router(webhook_router)
instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)



if __name__ == "__main__":
    try:
        asyncio.run(startup())
        uvicorn.run(app, host="0.0.0.0", port=8888)

    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n", traceback.format_exc())
        exit(1)
