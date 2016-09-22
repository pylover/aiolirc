
import asyncio

from aiolirc.tests.helpers import AioTestCase, EmulatedDispatcher
from aiolirc.dispatcher import Dispatcher


class TestDispatcher(AioTestCase):

    async def test_via_emulator(self):

        amp_power_call_count = 0
        amp_source_call_count = 0

        @Dispatcher.listen_for('amp power', repeat=5)
        async def amp_power(loop):
            nonlocal amp_power_call_count
            amp_power_call_count += 1

        @Dispatcher.listen_for('amp source', repeat=5)
        async def amp_source(loop):
            nonlocal amp_source_call_count
            amp_source_call_count += 1

        dispatcher = EmulatedDispatcher()

        try:
            await dispatcher.fill()
            await dispatcher.capture(exit_on_eof=True)
        except asyncio.QueueEmpty:
            pass

        self.assertEqual(amp_power_call_count, 2)
        self.assertEqual(amp_source_call_count, 2)
