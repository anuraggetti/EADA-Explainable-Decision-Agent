"""
E.A.D.A Application Configuration
----------------------------------
Contains centralized configuration values used throughout
the application.
"""

import os
from pathlib import Path


# Absolute project root
BASE_DIR = Path(__file__).resolve().parent


def get_boolean_env(name: str, default: bool = False) -> bool:
    """
    Read a Boolean environment variable safely.

    Accepted true values:
    1, true, yes, on
    """

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


class Config:
    """
    Base Flask and E.A.D.A configuration.
    """

    # Application information
    APP_NAME = "E.A.D.A"
    VERSION = "1.0.0"

    # Flask configuration
    SECRET_KEY = os.getenv(
        "EADA_SECRET_KEY",
        "eada-development-secret-key"
    )

    JSON_SORT_KEYS = False

    # AI training configuration
    TRAINING_EPISODES = int(
        os.getenv(
            "EADA_TRAINING_EPISODES",
            "100"
        )
    )

    LEARNING_RATE = float(
        os.getenv(
            "EADA_LEARNING_RATE",
            "0.10"
        )
    )

    DISCOUNT_FACTOR = float(
        os.getenv(
            "EADA_DISCOUNT_FACTOR",
            "0.90"
        )
    )

    EPSILON = float(
        os.getenv(
            "EADA_EPSILON",
            "0.20"
        )
    )

    DEFAULT_CONFIDENCE = int(
        os.getenv(
            "EADA_DEFAULT_CONFIDENCE",
            "75"
        )
    )

    # File and folder paths
    MODEL_FOLDER = BASE_DIR / "models"
    MODEL_PATH = MODEL_FOLDER / "q_table.json"

    DATABASE_FOLDER = BASE_DIR / "database"
    DATABASE_PATH = DATABASE_FOLDER / "database.db"

    GRAPH_FOLDER = BASE_DIR / "static" / "images"

    DATASET_FOLDER = BASE_DIR / "dataset"
    TRAINING_DATASET_PATH = (
        DATASET_FOLDER / "training_tasks.csv"
    )

    # Flask server configuration
    HOST = os.getenv(
        "EADA_HOST",
        "127.0.0.1"
    )

    PORT = int(
        os.getenv(
            "EADA_PORT",
            "5000"
        )
    )

    DEBUG = get_boolean_env(
        "EADA_DEBUG",
        True
    )

    USE_RELOADER = get_boolean_env(
        "EADA_USE_RELOADER",
        False
    )

    @classmethod
    def create_required_directories(cls) -> None:
        """
        Create folders required by the application.
        """

        required_directories = [
            cls.MODEL_FOLDER,
            cls.DATABASE_FOLDER,
            cls.GRAPH_FOLDER,
            cls.DATASET_FOLDER
        ]

        for directory in required_directories:
            directory.mkdir(
                parents=True,
                exist_ok=True
            )


class DevelopmentConfig(Config):
    """
    Development configuration.
    """

    DEBUG = True
    USE_RELOADER = False


class ProductionConfig(Config):
    """
    Production configuration.
    """

    DEBUG = False
    USE_RELOADER = False


# Temporary compatibility constants.
# Existing modules can continue importing these values until
# they are upgraded in their respective module stages.

APP_NAME = Config.APP_NAME
VERSION = Config.VERSION

TRAINING_EPISODES = Config.TRAINING_EPISODES

LEARNING_RATE = Config.LEARNING_RATE
DISCOUNT_FACTOR = Config.DISCOUNT_FACTOR
EPSILON = Config.EPSILON

MODEL_PATH = str(Config.MODEL_PATH)
DATABASE_PATH = str(Config.DATABASE_PATH)
GRAPH_FOLDER = str(Config.GRAPH_FOLDER)
TRAINING_DATASET_PATH = str(
    Config.TRAINING_DATASET_PATH
)

DEFAULT_CONFIDENCE = Config.DEFAULT_CONFIDENCE