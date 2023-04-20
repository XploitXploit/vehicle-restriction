from typing import Dict
from pydantic import BaseSettings, BaseModel


class Settings(BaseSettings):
    SQL_PATH: str = "app/queries"
    PUG_PATH: str = "app/db"

    AWTOSUITE_CONN: str = ""
    PRODUCTION_CONN: str = ""
    DWH_CONN: str = ""
    LOG_CONN: str = ""

    CONNECTION_DICT: Dict[str, str] = {
        "dwh": "DWH_CONN",
        "production": "PRODUCTION_CONN",
        "awtosuite": "AWTOSUITE_CONN",
        "log": "LOG_CONN",
    }

    TESTING: bool = False
    TESTING_USER_ID: int = 0
    API_KEYS: list = []
    DEBUG_MODE: bool = True
    GOWGO_AUTH: str = ""
    GOWGO_USER: str = ""
    GOWGO_PASSWORD: str = ""
    MS_NOTIFICATION_URI: str = ""
    MS_MODIFY_STATUS_URI: str = ""
    MS_LOGIN_URI: str = ""
    MS_LOGIN_TOKEN: str = ""

    REDIS_HOST: str = "localhost"

    VEHICLE_STATUS_FILTER: list = []

    TIME_ZONE: str = "America/Santiago"

    NOTIFICATION_TEMPLATE_NAME: str = ""

    TIMESPAN_ONGOING_MESSAGES_HOURS: int = 2

    class Config:
        env_file = "debugging.env"
        env_file_encoding = "utf-8"


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "vehicle_restriction"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    }
    loggers = {
        "vehicle_restriction": {"handlers": ["default"], "level": LOG_LEVEL},
    }


# CR: I'm not sure, but I think that this is a bad pattern. if the setting object is a
# module attribute it must be shared and it is harder to patch for testing.
settings = Settings()
logconfig = LogConfig()
