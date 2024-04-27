
from logging.config import dictConfig

from app.config.settings import settings


def configure_logging() -> None:
    dictConfig({
        'version': 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 32 if settings.PRODUCTION else 8,
                "default_value": "-"
            }
        },
        'formatters': {
            'console': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': '[%(correlation_id)s] %(name)s:%(lineno)s | %(message)s',
            },
            'file': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': '%(asctime)s %(levelname)s | [%(correlation_id)s] %(name)s:%(lineno)s | %(message)s',
            }
        },
        'handlers': {
            'default': {
                'class': 'rich.logging.RichHandler',
                'level': 'DEBUG',
                'formatter': 'console',
                'filters': ['correlation_id'],
            },
            'rotating_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'app.log',
                'maxBytes': 1024 * 1024,
                'backupCount': 3,
                'level': 'INFO',
                'formatter': 'file',
                "encoding": "utf8",
                'filters': ['correlation_id'],
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "rotating_file"],
            },
            'app': {
                'level': 'INFO' if settings.PRODUCTION else 'DEBUG',
                'handlers': ['default', 'rotating_file'],
            },
        }
    })
