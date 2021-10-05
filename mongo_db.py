from mongoengine import connect
from mongoengine import Document, StringField, DateTimeField, IntField
from config import mongo_credentials

connect(**mongo_credentials, connect=False)


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


def mongo_insert_message(message):
    try:
        message = MessageModel(MESSAGE_ID=message.MESSAGE_ID,
                               MESSAGE_TYPE_ID=message.MESSAGE_TYPE_ID,
                               DEVICE_ID=message.DEVICE_ID,
                               MESSAGE_STATE_ID=message.MESSAGE_STATE_ID,
                               URI=message.URI,
                               RESPONSE_CODE=message.RESPONSE_CODE,
                               RESPONSE_BODY=message.RESPONSE_BODY,
                               REQUEST_DATE=message.REQUEST_DATE,
                               RESPONSE_DATE=message.RESPONSE_DATE)
        message.save()
        return True
    except Exception as e:
        print(e)


def mongo_get_done_messages():
    try:
        return MessageModel.objects.filter(MESSAGE_STATE_ID__ne=1).all()
    except Exception as e:
        print(e)


def mongo_get_undone_messages():
    try:
        return MessageModel.objects.filter(MESSAGE_STATE_ID=1).all()
    except Exception as e:
        print(e)


def mongo_get_messages():
    try:
        return MessageModel.objects.all()
    except Exception as e:
        print(e)


def mongo_delete_message(message):
    try:
        message.delete()
        return True
    except Exception as e:
        print(e)


def mongo_get_message(device_id):
    try:
        return MessageModel.objects.filter(DEVICE_ID=device_id, MESSAGE_STATE_ID=1).first()
    except Exception as e:
        print(e)
