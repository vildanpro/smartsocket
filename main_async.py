from datetime import datetime
import asyncio
import json
from time import sleep

import aiohttp
import config
from db import get_new_messages, update_message_if_response_code_200, update_message_with_exception

timeout = aiohttp.ClientTimeout(total=config.request_device_timeout)


def date_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


async def async_request(message, session):
    message_id = message['MESSAGE_ID']
    request_date = date_now()
    try:
        async with session.get(url=message['URI'], timeout=timeout) as r:
            data = {
                'message_id': message['MESSAGE_ID'],
                'request_date': request_date,
                'response_date': date_now(),
                'response_body': str(await r.json()).replace("'", '"')
            }
            update_message_if_response_code_200(data=data)
    except Exception as e:
        print(e)
        data = {'message_id': message_id,
                'response_code': 408,
                'request_date': request_date,
                'response_body': json.dumps({"Exception": str(e).replace("'", '')})}
        update_message_with_exception(data=data)


async def main():
    tasks = list()
    print('NEW TASK LIST')
    async with aiohttp.ClientSession() as session:
        print('NEW SESSION')
        messages = get_new_messages()
        for message in messages:
            print('MESSAGE_ID: {MESSAGE_ID},\n'
                  'DEVICE_ID: {DEVICE_ID},\n'
                  'URI: {URI},\n'
                  'CREATED: {CREATED}\n'.format(**message))
            task = asyncio.create_task(async_request(message=message, session=session))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    while True:
        print('START NEW LOOP')
        asyncio.run(main())
