from code import InteractiveConsole

# to avoid ^[[A nonsense when pressing up arrow
import readline
import sys
from sqlalchemy import func
from sqlalchemy.sql import text


from mange.conf import settings
from mange.db import *
from mange.api import *

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
