import functools 
import logging
from time import sleep
from asyncio import iscoroutinefunction, sleep as async_sleep

from .exceptions import UnhandledException

logger = logging.getLogger(__name__)
RETRY_EVENT = object()

def with_retry() -> object:
    """
    # Resilienter Caller
    Decorator to retry a function on failure.

    Args:
        `opts` (dict, optional): A dictionary of options. Defaults to None.
        `opts_criteria` (function, optional): A function that returns the criteria to use for the `opts`. Defaults to None.
        `exceptions` (dict, optional): A dictionary of exceptions. Defaults to None.
        `retries` (int, optional): Number of retries. Defaults to False.
        `delay` (int, optional): Delay between retries. Defaults to 0.
        `on_retry` (function, optional): A function to call on each retry. Defaults to None.

    Returns:
        `object`: The decorated function.
    
    Example:
        >>> from requests import Response, request
        >>> from resilenter_caller import retry
        >>> 
        >>> @retry()
        >>> def send_request(url, method: str="GET", *args, **kwargs) -> Response:
        >>>     '''Sends an HTTP request to the specified URL and retries on failure.'''
        >>>     return request(method, url, *args, **kwargs)
        >>>
        >>> def example_custom_retry_403(response: Response) -> Response:
                print(f"Got response {response.status_code}")
                ...
                return RETRY_EVENT
        >>>
        >>> send_request(
                "https://www.google.com", retries=3, delay=5, 
                on_retry=lambda tries: print(f"Retry {tries}",
                opts={200: lambda r: r.status_code, 500: lambda r: RETRY_EVENT, 403: example_custom_retry_403}})
        >>> )
    """
    def decorator(f: object) -> object:
        if iscoroutinefunction(f):
            async def async_wrapper(*args, **kwargs) -> object:
                # Async wrapper logic
                opts, opts_base, exceptions, retries, delay, on_retry = kwargs.get("opts", None), kwargs.get("opts_criteria", None), \
                    kwargs.get("exceptions", None), kwargs.get("retries", False), kwargs.get("delay", 0), kwargs.get("on_retry", None)
                kwargs.pop("opts", None), kwargs.pop("opts_criteria", None), kwargs.pop("exceptions", None), kwargs.pop("retries", None), \
                    kwargs.pop("delay", None), kwargs.pop("on_retry", None)
                tries = 0
                while 1:
                    if retries and tries >= retries:
                        logger.error(f"Max retries reached for function {f.__name__}")
                        return None
                    elif tries > 0:
                        if on_retry: on_retry(tries)
                        logger.debug(f"Waiting {delay} seconds before retrying")
                        await async_sleep(delay)
                    try:
                        logger.debug(f"Executing function {f.__name__}")
                        response = await f(*args, **kwargs)
                        logger.debug(f"Got response ({response})") 
                        
                        if opts:
                            criteria = await opts_base(response) if opts_base else response
                            action = opts.get(criteria, None)
                            if action:
                                result = action(response)
                                if result == RETRY_EVENT:
                                    logger.debug(f"Got retry event ({result})")
                                    tries += 1
                                    continue
                                else:
                                    logger.debug(f"Got result ({result})")
                                    return result
                        return response
                    except Exception as e:
                        if exceptions:
                            action = exceptions.get(type(e), None)
                            if action or "all" in exceptions:
                                if action == RETRY_EVENT or (not action and "all" in exceptions and exceptions["all"] == RETRY_EVENT):
                                    logger.debug(f"Got retry event from exception {type(e).__name__}")
                                    tries += 1
                                    continue
                                result = await action(e) if action else await exceptions["all"](e)
                                if result == RETRY_EVENT:
                                    logger.debug(f"Got retry event ({result}) from exception {type(e).__name__}")
                                    tries += 1
                                    continue
                                else:
                                    logger.debug(f"Got result ({result}) from exception {type(e).__name__}")
                                    return result 
                        logger.error(f"Unhandled exception {type(e).__name__} ({e})")
                        raise UnhandledException(e)
            return async_wrapper
        else:
            def wrapper(*args, **kwargs) -> object:
                # Sync wrapper logic
                opts, opts_base, exceptions, retries, delay, on_retry = kwargs.get("opts", None), kwargs.get("opts_criteria", None), \
                    kwargs.get("exceptions", None), kwargs.get("retries", False), kwargs.get("delay", 0), kwargs.get("on_retry", None)
                kwargs.pop("opts", None), kwargs.pop("opts_criteria", None), kwargs.pop("exceptions", None), kwargs.pop("retries", None), \
                    kwargs.pop("delay", None), kwargs.pop("on_retry", None)
                tries = 0
                while 1:
                    if retries and tries >= retries:
                        logger.error(f"Max retries reached for function {f.__name__}")
                        return None
                    elif tries > 0:
                        if on_retry: on_retry(tries)
                        logger.debug(f"Waiting {delay} seconds before retrying")
                        sleep(delay)
                    try:
                        logger.debug(f"Executing function {f.__name__}")
                        response = f(*args, **kwargs)
                        logger.debug(f"Got response ({response})") 
                        
                        if opts:
                            criteria = opts_base(response) if opts_base else response
                            action = opts.get(criteria, None)
                            if action:
                                if action == RETRY_EVENT:
                                    logger.debug(f"Got retry event ({action})")
                                    tries += 1
                                    continue
                                result = action(response)
                                if result == RETRY_EVENT:
                                    logger.debug(f"Got retry event ({result})")
                                    tries += 1
                                    continue
                                else:
                                    logger.debug(f"Got result ({result})")
                                    return result
                        return response
                    except Exception as e:
                        if exceptions:
                            action = exceptions.get(type(e), None)
                            if action or "all" in exceptions:
                                if action == RETRY_EVENT or (not action and "all" in exceptions and exceptions["all"] == RETRY_EVENT):
                                    logger.debug(f"Got retry event from exception {type(e).__name__}")
                                    tries += 1
                                    continue
                                result = action(e) if action else exceptions["all"](e)
                                if result == RETRY_EVENT:
                                    logger.debug(f"Got retry event ({result}) from exception {type(e).__name__}")
                                    tries += 1
                                    continue
                                else:
                                    logger.debug(f"Got result ({result}) from exception {type(e).__name__}")
                                    return result 
                        logger.error(f"Unhandled exception {type(e).__name__} ({e})")
                        raise UnhandledException(e)
            return functools.wraps(f)(wrapper)
        
    return decorator