
import asyncio
import warnings

from aiolirc.lirc_client import LIRCClient


_commands = {}


def listen(func, cmd, *, repeat=1):
    if cmd not in _commands:
        _commands[cmd] = {}

    if repeat not in _commands[cmd]:
        _commands[cmd][repeat] = []

    _commands[cmd][repeat].append(func)


def listen_for(cmd, **kw):

    def _decorator(func):
        listen(func, cmd, **kw)
        return func

    return _decorator


def remove(func, cmd, *, repeat=1):
    _commands[cmd][repeat].remove(func)


class IRCDispatcher(object):

    def __init__(self, source: LIRCClient, loop: asyncio.BaseEventLoop=None):
        # Instance attributes
        self._source = source
        self._loop = loop or asyncio.get_event_loop()
        self._current_command_string = None
        self._current_command_repetition = 0

    async def listen(self) -> None:
        async for command_string in self._source:

            command = _commands.get(command_string)
            if not command:
                warnings.warn('Unknown command: %s' % command_string)
                self.reset_capturing_state()
                continue

            if command_string != self._current_command_string:
                # New command
                self.reset_capturing_state(command_string)

            # The same command is repeated.
            self._current_command_repetition += 1

            listeners = command.get(self._current_command_repetition)
            if listeners:
                async with self._source.ignore():
                    # reset counter
                    self.reset_capturing_state()
                    await asyncio.gather(*[l(self._loop) for l in listeners])

    def reset_capturing_state(self, cmd=None):
        self._current_command_string = cmd
        self._current_command_repetition = 0

