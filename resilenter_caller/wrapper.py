import functools
import logging
import asyncio
from time import time
from .exceptions import UnhandledException

logger = logging.getLogger(__name__)
RETRY_EVENT = object()

def with_retry(max_elapsed_time=None, backoff_strategy=None):
    def decorator(f):
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            config = {
                "conditions": kwargs.pop("conditions", None),
                "conditions_criteria": kwargs.pop("conditions_criteria", None),
                "exceptions": kwargs.pop("exceptions", None),
                "retries": kwargs.pop("retries", False),
                "delay": kwargs.pop("delay", 0),
                "on_retry": kwargs.pop("on_retry", None),
            }

            async def run_action(action, response):
                if callable(action):
                    num_args = action.__code__.co_argcount
                    if asyncio.iscoroutinefunction(action):
                        if num_args == 2:
                            return await action(response, tries)
                        else:
                            return await action(response)
                    else:
                        if num_args == 2:
                            return action(response, tries)
                        else:
                            return action(response)
                return action

            tries, start_time = 0, time()
            while 1:
                if max_elapsed_time and (time() - start_time) > max_elapsed_time:
                    logger.error(f"Max elapsed time reached for function {f.__name__}")
                    return None
                
                if config["retries"] and tries >= config["retries"]:
                    logger.error(f"Max retries reached for function {f.__name__}")
                    return None

                if tries > 0:
                    if config["on_retry"]:
                        config["on_retry"](tries)
                    logger.debug(f"Waiting {config['delay']} seconds before retrying")
                    await asyncio.sleep(config["delay"])
                    if backoff_strategy:
                        config["delay"] = backoff_strategy(tries)
                try:
                    logger.debug(f"Executing function {f.__name__}")
                    if asyncio.iscoroutinefunction(f):
                        response = await f(*args, **kwargs)
                    else:
                        response = await asyncio.to_thread(f, *args, **kwargs)
                    logger.debug(f"Got response ({response})")

                    if config["conditions"]:
                        criteria = config["conditions_criteria"](response) if config["conditions_criteria"] else response
                        action = config["conditions"].get(criteria, None) or config["conditions"].get("all", None)
                        if action:
                            result = await run_action(action, response)
                            if result == RETRY_EVENT:
                                logger.debug(f"Got retry event ({result})")
                                tries += 1
                                continue
                            else:
                                logger.debug(f"Got result ({result})")
                                return result
                    return response

                except Exception as e:
                    if config["exceptions"]:
                        action = config["exceptions"].get(type(e), None) or config["exceptions"].get("all", None)
                        if action:
                            result = await run_action(action, e)
                            if result == RETRY_EVENT:
                                logger.debug(f"Got retry event ({result}) from exception {type(e).__name__}")
                                tries += 1
                                continue
                            else:
                                logger.debug(f"Got result ({result}) from exception {type(e).__name__}")
                                return result

                    logger.error(f"Unhandled exception {type(e).__name__} ({e})")
                    raise UnhandledException(e)

        if asyncio.iscoroutinefunction(f):
            return async_wrapper
        else:
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return asyncio.run(async_wrapper(*args, **kwargs))

            return wrapper

    return decorator

resilient_call = with_retry