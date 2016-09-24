
import asyncio

from aiolirc.tests.helpers import AioTestCase, EmulatedClient


class TestLIRCClient(AioTestCase):

    async def test_via_emulator(self):
        async with await EmulatedClient(check_interval=.01) as client:
            for i in range(10):
                self.assertEqual(await client.__anext__(), 'amp power')

            for i in range(5):
                self.assertEqual(await client.__anext__(), 'amp source')

            for i in range(5):
                self.assertEqual(await client.__anext__(), 'off')

            for i in range(2):
                self.assertEqual(await client.__anext__(), 'amp source')

            async with client.ignore():
                await asyncio.sleep(.1)

            await self.assertRaises(asyncio.QueueEmpty, client.__anext__)


