import asyncio
import inspect


def _get_or_create_event_loop():
    try:
        asyncio.get_running_loop()
        return asyncio.get_event_loop()
    except RuntimeError:
        # The OS thread is not main
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def sync_run(coro, loop=None):
    assert inspect.iscoroutine(coro)
    loop = loop or _get_or_create_event_loop()
    if loop.is_running():
        return coro
    return loop.run_until_complete(coro)
