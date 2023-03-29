'''
Example 8: Custom backoff strategy (exponential backoff)

In this example, we will create a function that will randomly fail with a 30% chance.
If it fails, we will retry the function with an exponential backoff strategy.
'''
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
