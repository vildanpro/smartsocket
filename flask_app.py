from flask import Flask, render_template_string, request, redirect, url_for
from db import DB
from send_messages_to_devices import add_messages
from mikrotik_api import get_dhcp_leases


app = Flask(__name__)
db = DB()

template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" 
            integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        <meta charset="UTF-8">
        <title>SmartSocket</title>
    </head>
    <body>
        <form action='/'>
            {% for message_type_id in message_types %}
                <input type="submit" name='{{message_type_id['MESSAGE_TYPE_ID']}}' 
                value='{{message_type_id['MESSAGE_TYPE_NAME']}}' placeholder='{{message_type_id['DESCRIPTION']}}'>
                <br>
            {% endfor %}
        </form>
    </body>
    </html>
"""


@app.route("/")
def index():
    message_types = db.get_messages_types()
    for message_type in message_types:
        message_type_id = message_type['MESSAGE_TYPE_ID']
        if request.args.get(str(message_type_id)):
            add_messages(get_dhcp_leases(), message_type_id)
            return redirect(url_for('index'))

    return render_template_string(template, message_types=message_types)


if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.93.90')
