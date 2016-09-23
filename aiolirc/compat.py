

import functools
import sys

if sys.version_info < (3, 5, 2):
    def aiter_compat(instance):
        @functools.wraps(instance.__aiter__)
        async def wrapper(self):
            return self
        return wrapper
else:
    def aiter_compat(instance):
        return instance

