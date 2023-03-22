'''
Example 4: File processing with retry and custom handling

In this example, we will use the with_retry() decorator to implement a function 
that processes a file and retries the operation in case of failure. We will also 
use all the available options to customize the handling of different file sizes.
'''
import os
from resilenter_caller import with_retry, RETRY_EVENT

def process_large_file(file_path):
    print(f"Processing large file: {file_path}")
    return RETRY_EVENT

def process_small_file(file_path):
    print(f"Processing small file: {file_path}")
    return RETRY_EVENT

def process_valid_file(file_path):
    print(f"Processing valid file: {file_path}")
    return file_path

@with_retry()
def process_file(file_path):
    file_size = os.path.getsize(file_path)
    return file_size

if __name__ == "__main__":
    processed_file = process_file(
        "example.txt",
        retries=5,
        delay=2,
        opts={-1: process_large_file, 1: process_small_file},
        opts_criteria=lambda file_size: -1 if file_size > 1000000 else 1 if file_size < 1000 else 0,
        on_retry=lambda tries: print(f"Retry {tries}")
    )