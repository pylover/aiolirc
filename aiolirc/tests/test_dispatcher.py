
import asyncio

from aiolirc.tests.helpers import AioTestCase
from aiolirc.dispatcher import Dispatcher


class TestDispatcher(AioTestCase):

    @staticmethod
    async def get_emulation_queue():
        emulator_stack = asyncio.Queue()

        for i in range(10):
            await emulator_stack.put(('amp', 'power'))

        for i in range(5):
            await emulator_stack.put(('amp', 'source'))

        for i in range(50):
            await emulator_stack.put(None)

        for i in range(5):
            await emulator_stack.put(('amp', 'source'))

        async def _next():
            return emulator_stack.get_nowait()
        return _next

    async def test_via_emulator(self):

        amp_power_call_count = 0
        amp_source_call_count = 0

        @Dispatcher.listen_for('amp', 'power', repeat=5)
        async def amp_power(loop):
            nonlocal amp_power_call_count
            amp_power_call_count += 1

        @Dispatcher.listen_for('amp', 'source', repeat=5)
        async def amp_source(loop):
            nonlocal amp_source_call_count
            amp_source_call_count += 1

        dispatcher = Dispatcher(None, None, emulator=await self.get_emulation_queue())

        try:
            await dispatcher.capture()
        except asyncio.QueueEmpty:
            pass

        self.assertEqual(amp_power_call_count, 2)
        self.assertEqual(amp_source_call_count, 2)
