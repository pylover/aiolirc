
import asyncio

import lirc

from aiolirc.compat import aiter_compat


class LIRCClient(asyncio.Lock):
    _last_code = None
    emulator = None
    lircrc_prog = None
    lircrc_file = None
    check_interval = .05

    def __init__(self, lircrc_file, lircrc_prog, *, loop=None, emulator=None, check_interval=.05):
        self.lircrc_file = lircrc_file
        self.lircrc_prog = lircrc_prog
        self.emulator = emulator
        self.check_interval = check_interval
        asyncio.Lock.__init__(self, loop=loop)

    # Asynchronous Context Manager
    async def __aenter__(self):
        await super().__aenter__()
        if self.emulator:
            self._next_raw = self.emulator
        else:
            self.lirc_socket_id = lirc.init(self.lircrc_prog, config_filename=self.lircrc_file, blocking=False)
            await asyncio.sleep(.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print('Cleanup')
        if not self.emulator:
            lirc.deinit()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    # Asynchronous Iterator
    @staticmethod
    async def _next_raw():
        code = lirc.nextcode()
        if code:
            return tuple(code)
        return None

    @aiter_compat
    def __aiter__(self):
        return self

    async def __anext__(self):
        empty = 0
        while True:
            code = await self._next_raw()

            if code is None:

                if self._last_code is not None:
                    empty += 1

                if empty < 5:
                    await asyncio.sleep(self.check_interval)
                    continue

            self._last_code = code
            return code
