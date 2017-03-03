
import asyncio

from lirc import AsyncConnection, LircdConnection

from aiolirc.dispatcher import IRCDispatcher, listen, listen_for, remove


__version__ = '0.1.2'


async def quickstart(program, loop, **kwargs):
    connection = LircdConnection(program, **kwargs)
    async with AsyncConnection(connection, loop) as client:
        await IRCDispatcher(connection).listen()


def very_quickstart(program, **kwargs) -> int:
    main_loop = asyncio.get_event_loop()
    try:
        main_loop.run_until_complete(quickstart(program, main_loop, **kwargs))
    except KeyboardInterrupt:
        print('CTRL+C detected. terminating...')
        return 1
    finally:
        if not main_loop.is_closed():
            main_loop.close()
