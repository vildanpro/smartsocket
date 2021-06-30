from flask import Flask, render_template_string, request
from db import get_messages_types


app = Flask(__name__)


template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
        {% for message_type_id in message_types_id %}
        
            <input type="submit" name="{{message_type_id.message_type_id}}" 
            value="{{message_type_id.message_type_name}}">
        {% endfor %}
    </body>
    </html>
"""


@app.route("/", methods=['GET', 'POST'])
def control():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Do Something':
            pass  # do something
        elif request.form['submit_button'] == 'Do Something Else':
            pass  # do something else
        else:
            pass  # unknown
    elif request.method == 'GET':
        message_types_id = get_messages_types()
        return render_template_string(template, context=message_types_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.93.35')
