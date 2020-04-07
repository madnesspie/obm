# Copyright 2020 Alexander Polishchuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This magical module will rewrite all public methods in the public interface
of the library so they can run the loop on their own if it's not already
running. This rewrite may not be desirable if the end user always uses the
methods they way they should be ran, but it's incredibly useful for quick
scripts and the runtime overhead is relatively low.
"""
import asyncio
import functools
import inspect

from obm import mixins, models

__all__ = ["models", "mixins"]


def _syncify_wrap(_type, method_name):
    method = getattr(_type, method_name)

    @functools.wraps(method)
    def syncified(*args, **kwargs):
        coro = method(*args, **kwargs)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return coro
        return loop.run_until_complete(coro)

    # Save an accessible reference to the original method
    syncified.asynchronous = method
    setattr(_type, method_name, syncified)


def syncify(*types):
    """Converts all async methods in given types into synchronous.

    Converted methods return either the coroutine or the result
    based on whether asyncio's event loop is running.
    """
    for _type in types:
        for name in dir(_type):
            if not name.startswith("_") or name == "__call__":
                if inspect.iscoroutinefunction(getattr(_type, name)):
                    _syncify_wrap(_type, name)


syncify(mixins.ConnectorMixin)
