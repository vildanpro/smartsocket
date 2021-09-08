from mongoengine import connect
from mongoengine import Document, StringField, DateTimeField, IntField


connect(db='tasmota', host="192.168.93.90", port=27017, connect=False)


class MessageModel(Document):
    MESSAGE_ID = IntField()
    MESSAGE_TYPE_ID = IntField()
    DEVICE_ID = IntField()
    MESSAGE_STATE_ID = IntField()
    URI = StringField()
    RESPONSE_CODE = IntField()
    RESPONSE_BODY = StringField()
    REQUEST_DATE = DateTimeField()
    RESPONSE_DATE = DateTimeField()
    # meta = {'strict': False}
