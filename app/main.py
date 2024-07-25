from fastapi import FastAPI
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config.database import create_tables, drop_tables
from app.config.settings import settings
from app.config.redis import get_redis, get_cache
from app.config.logging_conf import configure_logging

from app.api_routes import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    configure_logging()
    app.state.redis = await get_redis()

    # await create_tables()
    try:
        # await drop_tables()
        await create_tables()
    except Exception as err:
        logger.error(
            'Failed to connect database. "Check if the virtual env is activated."')
        logger.error(f'{err.__class__}: {err}')

    yield
    # shutdown
    await app.state.redis.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    contact={
        'name': 'Md Salah',
        'email': 'mdsalah.connect@gmail.com',
    },
    license_info={
        'name': 'MIT'
    },
    lifespan=lifespan,
    root_path='/api/v1'
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(api_router)
