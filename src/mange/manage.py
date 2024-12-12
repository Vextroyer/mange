from mange.db import create_db
from mange.conf import settings
import sys

def get_command(command: list=sys.argv[1]):
    """Macros to manage the db"""
    if command == "shell":
        import mange.test.shell

    elif command == "migrate":
        create_db(settings.DATABASES["default"]["engine"])
        

    elif command == "test":
        from mange.test import test_db
        test_db.run()

    elif command == "runserver":
        from mange.server import runserver
        runserver()

if __name__ == "__main__":
    get_command()
