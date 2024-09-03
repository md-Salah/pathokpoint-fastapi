
import os
from logging.config import dictConfig
from datetime import datetime
from logging import Formatter
import pytz

from app.config.settings import settings

class BangladeshTimeFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        return datetime.fromtimestamp(record.created, pytz.utc).astimezone(pytz.timezone('Asia/Dhaka'))

def configure_logging() -> None:
    log_path = os.path.join('logs', 'app.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
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
                '()': BangladeshTimeFormatter,
                'datefmt': '%Y-%b-%d %I:%M:%S %p',
                'format': '[%(correlation_id)s] %(name)s:%(lineno)s | %(message)s',
            },
            'file': {
                '()': BangladeshTimeFormatter,
                'datefmt': '%Y-%b-%d %I:%M:%S %p',
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
                'filename': log_path,
                'maxBytes': 1024 * 1024,
                'backupCount': 10,
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
            "sqlalchemy": {
                "handlers": ["default", "rotating_file"],
            }
        }
    })
