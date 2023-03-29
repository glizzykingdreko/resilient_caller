'''
Example 9: Pass the number of tries to the action function

In this example, by using a function that takes 2 arguments, we 
can pass the number of tries to the action function.
'''
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
