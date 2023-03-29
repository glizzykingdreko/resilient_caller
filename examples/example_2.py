'''
Example 2: Asynchronous email sending with retry

In this example, we will use the resilient_call() decorator to implement an asynchronous 
function that sends an email and retries with a delay and a log message in case of failure.
'''
import aiosmtplib, asyncio
from email.message import EmailMessage
from resilient_caller import resilient_call, RETRY_EVENT

@resilient_call()
async def async_send_email(from_addr, to_addr, subject, body):
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = from_addr
    message["To"] = to_addr

    async with aiosmtplib.SMTP("smtp.example.com", 587) as server:
        await server.starttls()
        await server.login("your_email@example.com", "your_password")
        await server.send_message(message)

async def handle_send_error(e):
    print(f"Failed to send email: {e}")
    return RETRY_EVENT

async def main():
    await async_send_email(
        "you@example.com", "recipient@example.com", "Subject", "Message body", 
        retries=3,
        delay=5,
        exceptions={"all": handle_send_error}
    )

if __name__ == "__main__":
    asyncio.run(main())