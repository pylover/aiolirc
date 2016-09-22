
import asyncio

import lirc

from aiolirc.compat import aiter_compat


class LIRCClient(asyncio.Lock):

    def __init__(self, lircrc_file, lircrc_prog, *, loop=None, check_interval=.05, max_stack_size=10):
        self.lircrc_file = lircrc_file
        self.lircrc_prog = lircrc_prog
        self.check_interval = check_interval
        self._stack = asyncio.Queue(maxsize=10)
        self._last_code = None
        asyncio.Lock.__init__(self, loop=loop)

    # Asynchronous Context Manager
    async def __aenter__(self):
        await super().__aenter__()
        self.lirc_socket_id = lirc.init(self.lircrc_prog, config_filename=self.lircrc_file, blocking=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        lirc.deinit()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def _next_raw(self):
        if self._stack.empty():
            codes = lirc.nextcode()
            try:
                for code in codes:
                    self._stack.put_nowait(code)
            except asyncio.QueueFull:
                # Just ignoring future commands, until the queue freed-up.
                pass

        try:
            return self._stack.get_nowait()
        except asyncio.QueueEmpty:
            return None

    # Asynchronous Iterator
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
