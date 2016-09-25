
import asyncio

from aiolirc.lirc_client import LIRCClient
from aiolirc.dispatcher import IRCDispatcher, listen, listen_for, remove


__version__ = '0.1.1'


async def quickstart(*args, **kwargs):
    async with LIRCClient(*args, **kwargs) as client:
        await IRCDispatcher(client).listen()


def very_quickstart(*args, **kwargs) -> int:
    main_loop = asyncio.get_event_loop()
    try:
        main_loop.run_until_complete(quickstart(loop=main_loop))
    except KeyboardInterrupt:
        print('CTRL+C detected. terminating...')
        return 1
    finally:
        if not main_loop.is_closed():
            main_loop.close()
