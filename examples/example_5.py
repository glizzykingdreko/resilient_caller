'''
Example 5: Making an API request using a custom proxy and handling connection/proxy errors

In this example, we will use the send_request() function along with the update_session_proxy() 
function from the module to make an API request using a custom proxy. 
We will also handle connection and proxy errors.
'''
from requests import Session
from requests.exceptions import ProxyError, RequestException
from resilient_caller import send_request, RETRY_EVENT
from resilient_caller.utils import update_session_proxy

def handle_proxy_error(exception):
    print(f"A proxy error occurred: {exception}")
    return RETRY_EVENT

def handle_request_exception(exception):
    print(f"A connection error occurred: {exception}")
    return RETRY_EVENT

if __name__ == "__main__":
    # Create a new session
    session = Session()

    # Update the session proxy
    update_session_proxy(session, "123.45.67.89:8080")

    # Make an API request using the custom proxy
    response = send_request(
        "https://api.example.com/data",
        method="GET",
        # proxy="123.45.67.89:8081", # This will override the proxy set in the session
        session=session,
        retries=3,
        delay=2,
        exceptions={ProxyError: handle_proxy_error, RequestException: handle_request_exception},
        on_retry=lambda tries: print(f"Retry {tries}")
    )
    if response:
        print(response.json())
