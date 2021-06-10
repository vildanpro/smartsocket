import json
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from queries import get_devices
from device_request import do_device_request


db_path = os.path.abspath(os.getcwd()) + '/sqlite.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{db_path}'
db = SQLAlchemy(app)


class Device(db.Model):
    device_id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(80), unique=True, nullable=False)
    mac = db.Column(db.String(120), unique=True, nullable=False)
    updated = db.Column(db.Date)
    ip = db.Column(db.String)
    signal = db.Column(db.Integer)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Device %r>' % self.device_name


@app.route('/devices')
def show_devices():
    devices = get_devices()
    return render_template('devices.html', devices=devices)


@app.route('/devices_signal')
def show_devices_with_signal():
    devices_main_db = get_devices()

    for device in devices_main_db:
        exist_device = Device.query.filter_by(device_id=device.device_id).first()
        if not exist_device:
            new_device = Device(device_id=device.device_id,
                                device_name= device.device_name,
                                mac=device.mac,
                                updated=device.updated,
                                ip=device.ip)
            db.session.add(new_device)
            db.session.commit()

    devices_sqlite = Device.query.all()

    for device in devices_sqlite:
        ip = device.ip
        uri = f'http://{ip}/cm?cmnd=State'
        response_data = do_device_request(uri, timeout=3).response_data
        if response_data:
            data = json.loads(response_data)
            signal = data['Wifi']['Signal']
            update_device = Device.query.filter_by(device_id=device.device_id).update({'signal': signal})
            db.session.commit()
        else:
            signal = 0
            update_device = Device.query.filter_by(device_id=device.device_id).update({'signal': signal})
            db.session.commit()
    return render_template('devices_with_signal.html', devices=devices_sqlite)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
