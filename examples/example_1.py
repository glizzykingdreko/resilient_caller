'''
Example 1: Web scraping with retry, custom handling and handling for all exceptions

In this example, we will use the send_request() function provided in the module to perform 
web scraping. We will also use all the available options to customize the handling of 
different HTTP response codes and handle all exceptions.
'''
from bs4 import BeautifulSoup
from resilenter_caller import send_request, RETRY_EVENT

def handle_success(response):
    print(f"Request successful, status code: {response.status_code}")
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    print(f"Page title: {title.string}")
    return response

def handle_not_found(response):
    print(f"Page not found, status code: {response.status_code}")
    return RETRY_EVENT

def handle_server_error(response):
    print(f"Server error, status code: {response.status_code}")
    return RETRY_EVENT

def handle_all_exceptions(exception):
    print(f"An exception occurred: {type(exception).__name__} - {exception}")
    return RETRY_EVENT

if __name__ == "__main__":
    response = send_request(
        "https://www.example.com",
        retries=3,
        delay=2,
        opts={200: handle_success, 404: handle_not_found, 500: handle_server_error},
        exceptions={"all": handle_all_exceptions},
        on_retry=lambda tries: print(f"Retry {tries}")
    )
