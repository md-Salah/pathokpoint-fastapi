
from logging.config import dictConfig

from app.config.settings import settings

def configure_logging() -> None:
    dictConfig({
        'version': 1,
        "disable_existing_loggers": False,
        'formatters': {
            'default': {
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': '%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'console.log',
                'level': 'INFO',
                'formatter': 'default',
            }
        },
        'root': {
            'level': 'INFO' if settings.PRODUCTION else 'DEBUG',
            'handlers': ['console', 'file'],
        },
    })
