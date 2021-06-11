import asyncio
import json
import aiohttp
from device_request import double_quote, current_date
from queries import get_new_messages, update_message_if_response_code_200, update_message_with_exception


timeout_sec = 30
timeout = aiohttp.ClientTimeout(total=timeout_sec)


async def async_request(message, session, request_date):
    url = message.uri
    try:
        async with session.get(url=url, timeout=timeout) as r:
            data = {
                'message_id': message.message_id,
                'request_date': request_date,
                'response_date': current_date(),
                'response_body': double_quote(await r.json())
            }
            update_message_if_response_code_200(data=data)
    except Exception as e:
        print(e)
        data = {'message_id': message.message_id,
                'response_code': 408,
                'request_date': request_date,
                'response_body': json.dumps({"Exception": str(e).replace("'", '')})}
        update_message_with_exception(data=data)


async def main():
    tasks = list()
    async with aiohttp.ClientSession() as session:
        for message in messages:
            print(message)
            request_date = current_date()
            task = asyncio.create_task(async_request(message=message, session=session, request_date=request_date))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    while True:
        messages = get_new_messages()
        response_list = list()
        asyncio.run(main())
