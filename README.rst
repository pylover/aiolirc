

aiolirc
=======


.. image:: http://img.shields.io/pypi/v/aiolirc.svg
     :target: https://pypi.python.org/pypi/aiolirc

.. image:: https://img.shields.io/badge/license-GPLv3-brightgreen.svg
     :target: https://github.com/pylover/aiolirc/blob/master/LICENSE


Jump To
-------

 * `Documentation <http://aiolirc.dobisel.com>`_
 * `Python package index <https://pypi.python.org/pypi/aiolirc>`_
 * `Source on github <https://github.com/pylover/aiolirc>`_
 * `Downloads <https://pypi.python.org/pypi/aiolirc#downloads>`_


About
-----

Asynchronous messaging using python's new facility(async-await syntax), introduced in version 3.5 is so fun!

So, I decided to provide an asynchronous context manager and iterator wrapper for 
`Linux Infra-Red Remote Control(LIRC) <http://www.lirc.org/>`_.

Happily, the Cython is working well with asyncio. So the `lirc_client` C extension has been made by cython's extenstion
type. 

In addition, an `IRCDispatcher` type and a `listen_for` decorator have been provided.

Install
-------

::

     $ apt-get install liblircclient-dev python3.5-dev build-essential
     $ pip install cython
     $ pip install aiolirc


Quick Start
-----------

The simplest way to use this library is the famous `very_quickstart` function as follows::

    from aiolirc import very_quickstart, listen_for

    @listen_for('play')
    async def do_play(loop):
        ...
        # Do play stuff

    very_quickstart('my-prog')  # my-prog is configured in your lircrc file.


Another coroutine function named `quickstart` is also available.This lets you have control over the event loop 
life-cycle::

    import asyncio
    from aiolirc import quickstart

    main_loop = asyncio.get_event_loop()
    try:
        main_loop.run_until_complete(quickstart(loop=main_loop))
    except KeyboardInterrupt:
        print('CTRL+C detected. terminating...')
        return 1
    finally:
        if not main_loop.is_closed():
            main_loop.close()


The `IRCDispatcher`
-------------------
    
Constructor
^^^^^^^^^^^

::

    def __init__(self, source: LIRCClient, loop: asyncio.BaseEventLoop=None):


Example of usage
^^^^^^^^^^^^^^^^
::


    import asyncio
    
    from aiolirc.lirc_client import LIRCClient
    from aiolirc.dispatcher import IRCDispatcher, listen_for

    @listen_for('amp power', repeat=5)
    async def amp_power(loop):
        ...
        # Do your stuff

    @listen_for('amp source')
    async def amp_source(loop):
        ...
        # Do your stuff
                        

    async with LIRCClient('my-prog') as client:
        dispatcher = IRCDispatcher(client)
        await dispatcher.listen()


The `LIRCClient`
----------------

Constructor
^^^^^^^^^^^
::

    def __cinit__(self, lircrc_prog, *, lircrc_file='~/.config/lircrc', loop=None, check_interval=.05, verbose=False, 
        blocking=False):

To advance control over the messages received from lirc, asychronously iter over an instance of the `LIRCClient` after
calling `LIRCClient.lirc_init()`. And make sure the `LIRCClient.lirc_deinit()` has been called after finishing your work
with `LIRCClient`::

    from aiolirc.lirc_client import LIRCClient

    client = LIRCClient('my-prog')
    try:
        client.lirc_init()
        async for cmd in client:
            print(cmd)
    finally:
        client.lirc_deinit()
        


You may use the `LIRCClient` as an asynchronous context manager as described as follows, to automatically call the 
`LIRCClient.lirc_init()` and `LIRCClient.lirc_deinit()` functions, and also acquiring a lock to prevent multiple 
instances of the `LIRCClient` from reading messages from lirc_client wrapper::

    from aiolirc.lirc_client import LIRCClient
 
    async with LIRCClient('my-prog') as client:
        async for cmd in client:
            print(cmd)
        

Systemd
-------

Create a main.py::

     import sys
     import asyncio
     
     from aiolirc import IRCDispatcher, LIRCClient

     async def launch(self) -> int:

         async with LIRCClient('my-prog', lircrc_file='path/to/lircrc', check_interval=.06) as client:
             dispatcher = IRCDispatcher(client)
             result = (await asyncio.gather(dispatcher.listen(), return_exceptions=True))[0]

         if isinstance(result, Exception):
             raise result
             
         return 0
    
     def main(self):
          
         main_loop = asyncio.get_event_loop()
         try:
             return main_loop.run_until_complete(launch())
         except KeyboardInterrupt:
             print('CTRL+C detected.')
             return 1
         finally:
             if not main_loop.is_closed():
                 main_loop.close()
                 
     if __name__ == '__main__':
         sys.exit(main())


`/etc/systemd/system/aiolirc.service` file::

     [Unit]
     Description=aiolirc
     
     [Service]
     ExecStart=python3.5 /path/to/main.py
     User=user
     Group=group
     
     [Install]
     WantedBy=multi-user.target
     
systemctl::

     $ systemctl enable aiolirc
     $ systemctl start aiolirc
     $ systemctl restart aiolirc
     
     $ ps -Af | grep 'main.py'
     
     $ systemctl stop aiolirc

Change Log
----------

**0.1.0**

   - README.rst
