from mange.conf import settings
from mange.db import *
from mange.api import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

URL = settings.DATABASES["default"]["engine"]

client = Client(url=URL)

banner = """
#######################################
# mange database interactive console #
#######################################
A Client instance is already defined (as 'client') and connected to the database.
Use it to make queries.
"""
i = InteractiveConsole(locals=locals())
i.interact(banner=banner)
