import logging
import logging.config
from os import path, mkdir
from sys import stdout, version_info
from datetime import datetime
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger
LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = f"{__name__}/logs"

# Make Logs directory if it does not exixts
if not path.isdir(LOGDIR):
    mkdir(LOGDIR)

LOGFILE = f"{LOGDIR}/{__name__}_{LOG_DATETIME}_log.txt"

file_handler = FileHandler(filename=LOGFILE)
stdout_handler = StreamHandler(stdout)

logging.basicConfig(
    format="%(asctime)s - [Alita_Robot] - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[file_handler, stdout_handler],
)

logging.getLogger("pyrogram").setLevel(WARNING)
LOGGER = logging.getLogger(__name__)


# Set specific loggers' levels
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client
from database.ia_filterdb import Media2
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web

class LazyPrincessXBot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

LazyPrincessBot = LazyPrincessXBot()

multi_clients = {}
work_loads = {}
