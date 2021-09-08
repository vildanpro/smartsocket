def get_query_update_message(message):
    return f"UPDATE sockets.messages\n" \
                f"SET message_state_id = {message.MESSAGE_STATE_ID},\n" \
                f"\tresponse_code = {message.RESPONSE_CODE},\n" \
                f"\tresponse_body = '{message.RESPONSE_BODY}',\n" \
                f"\trequest_date = TO_DATE(\'{message.REQUEST_DATE}\', 'YYYY-MM-DD HH24:MI:SS'),\n" \
                f"\tresponse_date = TO_DATE('{message.RESPONSE_DATE}', 'YYYY-MM-DD HH24:MI:SS')\n" \
                f"WHERE message_id = {message.MESSAGE_ID}"


def get_query_devices():
    return 'SELECT * FROM sockets.devices ORDER BY device_id'


def get_query_new_oracle_messages():
    return 'SELECT m.MESSAGE_ID, m.MESSAGE_TYPE_ID, m.DEVICE_ID, m.MESSAGE_STATE_ID, m.URI, m.RESPONSE_CODE,\n' \
            '\t\tm.RESPONSE_BODY, m.REQUEST_DATE, m.RESPONSE_DATE\n' \
            'FROM (SELECT DEVICE_ID, MIN(MESSAGE_ID) AS MESSAGE_ID\n' \
            '\t\tFROM MESSAGES\n' \
            '\t\tWHERE MESSAGE_STATE_ID = 1\n' \
            '\t\tGROUP BY DEVICE_ID) n\n' \
            'JOIN MESSAGES m\n' \
            'ON n.MESSAGE_ID = m.MESSAGE_ID'
