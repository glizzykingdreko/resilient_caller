'''
Example 3: Reading temperature from a sensor with retry and custom handling

In this example, we will use the resilient_call() decorator to implement a function that reads 
the temperature from a sensor and retries the read operation in case of failure. We will also use 
all the available options to customize the handling of different temperature values.
'''
import random
from resilient_caller import resilient_call, RETRY_EVENT

class SensorError(Exception):
    pass

def read_temperature_from_sensor():
    # Simulate reading temperature from a sensor
    value = random.uniform(-20, 50)
    if value < -10:
        raise SensorError("Failed to read from sensor")
    return value

def handle_low_temperature(temp):
    print(f"Temperature is too low: {temp}")
    return RETRY_EVENT

def handle_high_temperature(temp):
    print(f"Temperature is too high: {temp}")
    return RETRY_EVENT

def handle_valid_temperature(temp):
    print(f"Temperature is within the valid range: {temp}")
    return temp

@resilient_call()
def get_temperature_data():
    return read_temperature_from_sensor()

if __name__ == "__main__":
    temperature_data = get_temperature_data(
        retries=5,
        delay=2,
        exceptions={SensorError: RETRY_EVENT},
        conditions={-1: handle_low_temperature, 1: handle_high_temperature},
        conditions_criteria=lambda temp: -1 if temp < 0 else 1 if temp > 30 else 0,
        on_retry=lambda tries: print(f"Retry {tries}")
    )
