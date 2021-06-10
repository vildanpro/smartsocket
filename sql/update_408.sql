UPDATE sockets.messages
SET message_state_id = 24,
    response_code = {response_code},
    request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS')
WHERE message_id = {message_id}