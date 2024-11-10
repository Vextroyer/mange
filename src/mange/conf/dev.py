from mange.conf._base import *

# Paths
TEST_DIR = Path(__file__).parent.parent / "test"
SAVES = TEST_DIR / "sav"

HOST = "localhost"
PORT = 14548

# Config
DEBUG = True

# Database
DATABASES = {
    "default": {
        "engine": "sqlite:///" + str(TEST_DIR / "test_db.sqlite3"),
    },
}

LOGGERS = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
            "formatter": "basic",
        },
        "audit_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 5000000,
            "backupCount": 1,
            "filename": BASE_DIR / "logs" / "api.error",
            "encoding": "utf-8",
            "formatter": "basic",
        },
    },
    "formatters": {
        "basic": {
            "style": "{",
            "format": "{asctime:s} [{levelname:s}] -- {name:s}: {message:s}",
        }
    },
    "loggers": {
        "user_info": {
            "handlers": (
                #   "console",
                "audit_file",
            ),
            "level": "INFO" if DEBUG is False else "DEBUG",
            # "level": "DEBUG",
        },
        "audit": {"handlers": ("audit_file",), "level": "ERROR"},
        "global": {
            "handlers": ("console",),
            "level": "INFO" if DEBUG is False else "DEBUG",
            # "level": "DEBUG",
        },
    },
}
