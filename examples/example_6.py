'''
Example 6: Asynchronous API call with rate limiting retry

In this example, we will use the with_retry() decorator to implement an 
asynchronous function that makes an API call and retries the call in case of failure or rate limiting.
'''
import aiohttp, asyncio
from resilenter_caller import with_retry, RETRY_EVENT

async def handle_rate_limit(e):
    print(f"Rate limited: {e}")
    return RETRY_EVENT

@with_retry()
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
