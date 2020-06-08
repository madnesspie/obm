import asyncio
import inspect


def sync_run(coro, loop=None):
    assert inspect.iscoroutine(coro)
    loop = loop or asyncio.get_event_loop()
    if loop.is_running():
        return coro
    return loop.run_until_complete(coro)
