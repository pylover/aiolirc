
import asyncio
import warnings

from aiolirc.lirc import LIRCClient


class Dispatcher(LIRCClient):

    # Class attributes
    _commands = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instance attributes
        self._current_command = None
        self._current_command_repetition = 0

    @classmethod
    def listen(cls, func, cmd, *, repeat=1):
        if cmd not in cls._commands:
            cls._commands[cmd] = {}

        if repeat not in cls._commands[cmd]:
            cls._commands[cmd][repeat] = []

        cls._commands[cmd][repeat].append(func)

    @classmethod
    def remove(cls, func, cmd, *, repeat=1):
        cls._commands[cmd][repeat].remove(func)

    async def check_for_event(self):
        """
        Checking for event if matched with any criteria stored in _commands.

        :return: True if need to continue to counting repetition, False for reset.
        """
        # Check for event

        command = self._commands[self._current_command]
        if not len(command):
            return False

        listeners = command.get(self._current_command_repetition)
        if listeners:
            await asyncio.gather(*[l(self._loop) for l in listeners])

        return max(command.keys()) > self._current_command_repetition

    @classmethod
    def listen_for(cls, cmd, **kw):

        def _decorator(func):
            cls.listen(func, cmd, **kw)
            return func

        return _decorator

    def reset_capturing_state(self):
        self._current_command = None
        self._current_command_repetition = 0

    async def feed_command(self, cmd):
        if cmd is None:
            self.reset_capturing_state()
            return

        if cmd not in self._commands:
            warnings.warn('Unknown comamnd: %s' % cmd)
            self.reset_capturing_state()
            return

        if cmd == self._current_command:
            # The same command is repeated.
            self._current_command_repetition += 1
        else:
            # New command
            self._current_command = cmd
            self._current_command_repetition = 1

        if not await self.check_for_event():
            # reset counter
            self._current_command_repetition = 0

    async def capture(self, exit_on_eof=False):
        async with self:
            async for command in self:
                if command is None:
                    await self.feed_command(None)
                    # Just for unittests
                    if exit_on_eof:
                        break
                    else:
                        continue

                await self.feed_command(command)