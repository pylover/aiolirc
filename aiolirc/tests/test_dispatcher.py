
import asyncio

from aiolirc.tests.helpers import AioTestCase, EmulatedClient
from aiolirc.dispatcher import IRCDispatcher, listen_for


class TestDispatcher(AioTestCase):

    async def test_via_emulator(self):

        amp_power_call_count = 0
        amp_source_call_count = 0

        @listen_for('amp power', repeat=5)
        async def amp_power(loop):
            nonlocal amp_power_call_count
            amp_power_call_count += 1

        @listen_for('amp source', repeat=5)
        async def amp_source(loop):
            nonlocal amp_source_call_count
            amp_source_call_count += 1

        async with EmulatedClient() as client:
            dispatcher = IRCDispatcher(client)

            try:
                await dispatcher.listen()
            except asyncio.QueueEmpty:
                print('Test Done')

        self.assertGreaterEqual(amp_power_call_count, 1)
        self.assertGreaterEqual(amp_source_call_count, 1)
