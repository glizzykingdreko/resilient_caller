from .wrapper import RETRY_EVENT, with_retry
from .utils import update_session_proxy
from requests import Session, Response

@with_retry()
def send_request(url, *args, **kwargs) -> Response:
    """Sends an HTTP request to the specified URL and retries on failure.
    
    Returns:
        Response: The response object returned by the `requests` function.
    """
    method = kwargs.get("method", "GET")
    if not kwargs.get("session", None): session = Session()
    kwargs.pop("session", None)
    if kwargs.get("proxies", None):
        # Automatically format the proxies in the correct format for the session
        # from a string input or directly pass a dictionary
        update_session_proxy(kwargs.get("proxies"))
        kwargs.pop("proxies")
    return session.request(method, url, *args, **kwargs)

