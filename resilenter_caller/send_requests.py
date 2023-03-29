from .wrapper import RETRY_EVENT, resilient_call
from .utils import update_session_proxy
from requests import Session, Response

@resilient_call()
def send_request(url, *args, method="GET", session=None, proxies=None, **kwargs) -> Response:
    """Sends an HTTP request to the specified URL and retries on failure.
    
    Returns:
        Response: The response object returned by the `requests` function.
    """
    if session is None:
        session = Session()

    if proxies:
        # Automatically format the proxies in the correct format for the session
        # from a string input or directly pass a dictionary
        update_session_proxy(proxies)

    return session.request(method, url, *args, **kwargs)
