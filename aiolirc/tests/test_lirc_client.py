import asyncio

from os.path import join, abspath, dirname

from aiolirc.tests.helpers import AioTestCase
from aiolirc.lirc import LIRCClient


class TestLIRCClient(AioTestCase):

    async def test_via_emulator(self):
        this_dir = abspath(dirname(__file__))
        lircrc_config_file = join(this_dir, 'conf', 'lircrc')
        print("Using lircrc file: %s" % lircrc_config_file)

        emulator_stack = asyncio.Queue()

        for i in range(10):
            await emulator_stack.put(('amp', 'power'))

        for i in range(5):
            await emulator_stack.put(('amp', 'source'))

        for i in range(50):
            await emulator_stack.put(None)

        for i in range(5):
            await emulator_stack.put(('amp', 'source'))

        async with LIRCClient(None, None, emulator=emulator_stack.get) as client:
            for i in range(10):
                self.assertEqual(await client.__anext__(), ('amp', 'power'))

            for i in range(5):
                self.assertEqual(await client.__anext__(), ('amp', 'source'))

            self.assertEqual(await client.__anext__(), None)

            for i in range(5):
                self.assertEqual(await client.__anext__(), ('amp', 'source'))
