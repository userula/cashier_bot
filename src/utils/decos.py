import asyncio
from functools import wraps
from typing import Tuple, Union, Type

from utils import Logger


def async_retry(exceptions_to_check: Union[Type[Exception], Tuple[Type[Exception], ...]], attempts: int = 4,
                delay: int = 2, back_off: int = 2, logger=Logger(name="async_retry").logger):
    def deco_retry(f):
        @wraps(f)
        async def f_retry(*args, **kwargs):
            nonlocal attempts, delay
            while attempts > 1:
                try:
                    return await f(*args, **kwargs)
                except exceptions_to_check as e:
                    logger.warning(msg=f"{e}, Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    attempts -= 1
                    delay *= back_off
            return await f(*args, **kwargs)
        return f_retry

    return deco_retry
