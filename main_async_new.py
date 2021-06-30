import json
from datetime import datetime

import aiohttp
import asyncio
import time

from db import get_new_messages, update_message_if_response_code_200


def date_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# async def get(url):
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(url) as response:
#                 return response
#         except Exception as e:
#             print(e)
#
# loop = asyncio.get_event_loop()
#
# coroutines = [get(message['URI']) for message in get_new_messages()]
#
# results = loop.run_until_complete(asyncio.gather(*coroutines))
#
# print("Results: %s" % results)


start_time = time.time()


async def device_request(message_id, session, url):
    async with session.get(url) as resp:
        print(message_id, url)
        request_date = date_now()
        device_json = await resp.json()
        response_date = date_now()
        if resp.status == 200:
            print(message_id, request_date, response_date, json.dumps(device_json), url)
            await update_message_if_response_code_200(message_id=message_id,
                                                      request_date=request_date,
                                                      response_date=response_date,
                                                      response_body=json.dumps(device_json))
        return message_id, resp.status


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for message in get_new_messages():
            url = message['URI']
            tasks.append(asyncio.ensure_future(device_request(message['MESSAGE_ID'], session, url)))

        device_responses = await asyncio.gather(*tasks)
        print(device_response for device_response in device_responses)


asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))
