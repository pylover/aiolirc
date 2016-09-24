from aiolirc.lirc_client import LIRCClient
from aiolirc.dispatcher import IRCDispatcher, listen, listen_for, remove

__version__ = '0.1.0'


async def quickstart(*args, **kwargs):
    async with LIRCClient(*args, **kwargs) as client:
        await IRCDispatcher(client).listen()
