# Resilient Caller

A Python package that provides a customizable wrapper to retry function calls with custom logic. This package was developed to address the need for executing numerous requests with similar, yet slightly different, exception handling. The wrapper reduces the need to write multiple while loops and try/except blocks for each request.

The wrapper can be implemented for any function, not just requests-related functions. The module also includes a Python requests implementation with auto proxy formatting from a string, by simply passing the proxy as a string to the send_request function. Async functions support as well.

The resilient caller supports the following keyword arguments (kwargs) for the wrapper. Note that these kwargs will not be passed to the wrapped function:

- `conditions`: A dictionary specifying the actions to take for a given outcome.
- `conditions_criteria`: The criteria to use when checking the `conditions`.
- `exceptions`: A dictionary specifying the actions to take for a given exception or 'all' for non-handled or all exceptions.
- `retries`: The maximum number of times to retry the function (disabled by default).
- `delay`: The number of seconds to sleep between retries.
- `on_retry`: A callback function to execute on retry, for example, a log function.
In the module, a Python requests implementation is provided with automatic proxy formatting from a string.

Please refer to the usage examples below and the examples folder in the repository for more information on how to use the resilient caller.
 
## Installation
Install the package using pip:
```
pip install resilient_caller
```

## Examples

### Quick simple and easy web scraping monitor
In this example, we will create a `SimpleScraper` class that monitors [glizzykingdreko's medium blog](https://medium.com/@glizzykingdreko) for new articles. By defining the start method with the `@resilient_call()` decorator and passing `delay=5` and `exceptions={"all": RETRY_EVENT}` when calling it, we ensure that the scraper handles all exceptions with a retry and adds a delay of 5 seconds between each request.
```python
from bs4 import BeautifulSoup
from requests import Session
from typing import List
from time import sleep
from resilenter_caller import resilient_call, RETRY_EVENT

class SimpleScraper:
    def __init__(self):
        self.session, self.articles = Session(), []
        # This is making the function run through a while loop with a delay of 5 seconds
        # and handling any exception with a retry event.
        self.start(delay=5, exceptions={"all": RETRY_EVENT})

    @resilient_call()
    def start(self) -> None:
        data = self.load_api_data()
        self.load_response_details(data)

    def load_response_details(self, response: str) -> List[str]:
        data = BeautifulSoup(response, "html.parser")
        new_articles = [
            [d.find("h2").text, d.find("a").get("href")] 
            for d in data.find_all("article") 
            if d.find("h2").text not in self.articles
        ]
        for article in new_articles:
            name, url = article
            print(f"New glizzykingdreko's article on medium \"{name}\"! Check it out at {url}.")
            self.articles.append(name)
        return new_articles

    def load_api_data(self) -> str:
        url = "https://medium.com/@glizzykingdreko"
        return self.session.get(url).text

if __name__ == "__main__":
    SimpleScraper()

```
### Web scraping with retry, custom handling and handling for all exceptions
In this example, we will use the send_request() function provided in the module to perform 
web scraping. We will also use all the available options to customize the handling of 
different HTTP response codes and handle all exceptions.
```python
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
        conditions={200: handle_success, 404: handle_not_found, 500: handle_server_error},
        exceptions={"all": handle_all_exceptions},
        on_retry=lambda tries: print(f"Retry {tries}")
    )
```

### File processing with retry and custom handling
In this example, we will use the resilient_call() decorator to implement a function 
that processes a file and retries the operation in case of failure. We will also 
use all the available options to customize the handling of different file sizes.

```python
import os
from resilenter_caller import resilient_call, RETRY_EVENT

def process_large_file(file_path):
    print(f"Processing large file: {file_path}")
    return RETRY_EVENT

def process_small_file(file_path):
    print(f"Processing small file: {file_path}")
    return RETRY_EVENT

def process_valid_file(file_path):
    print(f"Processing valid file: {file_path}")
    return file_path

@resilient_call()
def process_file(file_path):
    file_size = os.path.getsize(file_path)
    return file_size

if __name__ == "__main__":
    processed_file = process_file(
        "example.txt",
        retries=5,
        delay=2,
        conditions={-1: process_large_file, 1: process_small_file},
        conditions_criteria=lambda file_size: -1 if file_size > 1000000 else 1 if file_size < 1000 else 0,
        on_retry=lambda tries: print(f"Retry {tries}")
    )
```

### Asynchronous API call with rate limiting retry
In this example, we will use the resilient_call() decorator to implement an 
asynchronous function that makes an API call and retries the call in case of failure or rate limiting.
```python
import aiohttp, asyncio
from resilenter_caller import resilient_call, RETRY_EVENT

async def handle_rate_limit(e):
    print(f"Rate limited: {e}")
    return RETRY_EVENT

@resilient_call()
async def async_api_call(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 429:
                raise Exception("Rate limited")
            data = await response.json()
            return data

async def main():
    await async_api_call(
        "https://httpbin.org/status/429",
        retries=3, 
        delay=5,
        exceptions={Exception: handle_rate_limit}
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom backoff strategy (exponential backoff)
In this example, we will create a function that will randomly fail with a 30% chance.
If it fails, we will retry the function with an exponential backoff strategy.
```python
import logging
import random
from resilenter_caller import resilient_call, RETRY_EVENT

# Set level as debug to get full logs
logging.basicConfig(level=logging.DEBUG)

def exponential_backoff(tries):
    return 2 ** (tries - 1) + random.uniform(0, 1)

# If 2 arguments are passed to an exception function
# the second argument will be the number of tries
# (same thing for a condition)
def print_exception(exception, tries):
    print(f"Exception: {exception} (try {tries})")
    return RETRY_EVENT

@resilient_call()
def example_function():
    random_num = random.random()
    if random_num < 0.7:
        print("Failed, retrying...")
        raise ValueError("Random number too low")
    else:
        print("Success!")
        return "Successful response"

if __name__ == '__main__':
    result = example_function(
        retries=5, 
        on_retry=exponential_backoff,
        exceptions={ValueError: print_exception}
    )
    print("Result:", result)
```

### Pass the number of tries to the action function
In this example, by using a function that takes 2 arguments, we 
can pass the number of tries to the action function.
```python
import random
from resilenter_caller import resilient_call, RETRY_EVENT

def some_condition(response):
    return response == "Retry"

def handle_response(response, tries):
    if tries < 3 and some_condition(response):
        return RETRY_EVENT
    else:
        return response

# We set the max execution time to 10 seconds
@resilient_call(max_elapsed_time=10)
def example_function():
    random_num = random.random()
    if random_num < 0.6:
        print("Returning 'Retry'")
        return "Retry"
    else:
        print("Success!")
        return "Successful response"

if __name__ == '__main__':
    result = example_function(
        # With 'all' we can handle all the
        # possible responses or exceptions
        conditions={'all': handle_response},
    )
    print("Result:", result)
```
These examples demonstrate the versatility and usefulness of the Resilient Caller module. This module can be applied to a wide range of use cases, from web scraping and file processing to API calls and custom backoff strategies. Make sure to explore the examples folder in the repository for even more examples and use cases with other parameters and configurations.

## Personal Thoughts

I hope this module will help many developers save time and make their code more efficient. Please feel free to contact me for any help or suggestions via [Email](mailto:glizzykingdreko@protonmail.com) or [Twitter](https://mobile.twitter.com/glizzykingdreko). Don't forget to follow me on GitHub and Medium for more exciting content and updates. I appreciate your feedback and contributions to the project.

## Contributing
I welcome contributions to the Resilient Caller project! To contribute, please follow these steps:

- Fork the repository on GitHub.
- Create a new branch with a descriptive name.
- Make your changes, add new features, or fix bugs.
- Write tests to ensure that your changes work as expected.
- Update the documentation and examples to reflect your changes.
- Commit your changes and create a pull request.
Please make sure to follow the existing code style and provide clear, concise commit messages. If you have any questions, feel free to open an issue, and we'll be happy to help.

## License
This project is licensed under the MIT [License](LICENSE). See the LICENSE file for more details.

## My links
- [Project repository](https://github.com/glizzykingdreko/resilient_caller)
- [GitHub](https://github.com/glizzykingdreko)
- [Twitter](https://mobile.twitter.com/glizzykingdreko)
- [Medium](https://medium.com/@glizzykingdreko)
- [Email](mailto:glizzykingdreko@protonmail.com)
