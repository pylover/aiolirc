import asyncio

from aiolirc.client import LIRCClient


async def main():
    print('MAIN')
    async with LIRCClient('MyRPI') as c:
        async for cmd in c:
            print(cmd)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('CTRL+C')
    finally:
        if not loop.is_closed():
            loop.close()
