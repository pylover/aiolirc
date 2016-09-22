
from aiolirc.tests.helpers import AioTestCase, EmulatedDispatcher


class TestLIRCClient(AioTestCase):

    async def test_via_emulator(self):
        async with EmulatedDispatcher() as client:
            await client.fill()
            for i in range(10):
                self.assertEqual(await client.__anext__(), 'amp power')

            for i in range(5):
                self.assertEqual(await client.__anext__(), 'amp source')

            for i in range(5):
                self.assertEqual(await client.__anext__(), 'off')

            for i in range(5):
                self.assertEqual(await client.__anext__(), 'amp source')

            self.assertEqual(await client.__anext__(), None)
