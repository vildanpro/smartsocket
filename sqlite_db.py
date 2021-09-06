import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(f'sqlite:///{os.getcwd()}/messages.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()


class Message(Base):
    __tablename__ = "messages"
    MESSAGE_ID = Column(Integer, primary_key=True)
    MESSAGE_TYPE_ID = Column(Integer)
    DEVICE_ID = Column(Integer)
    MESSAGE_STATE_ID = Column(Integer)
    URI = Column(VARCHAR)
    RESPONSE_CODE = Column(Integer)
    RESPONSE_BODY = Column(VARCHAR)
    REQUEST_DATE = Column(Date)
    RESPONSE_DATE = Column(Date)


def sqlite_insert_oracle_messages(oracle_messages):
    try:
        for oracle_message in oracle_messages:
            if not session.query(Message).get(oracle_message['MESSAGE_ID']):
                session.add(Message(**oracle_message))
        session.commit()
    except Exception as e:
        print(e)


def sqlite_remove_message(message):
    try:
        delete_message = session.query(Message).get(message.MESSAGE_ID)
        session.delete(delete_message)
        session.commit()
        return True
    except Exception as e:
        print(e)


def sqlite_get_message(device_id):
    try:
        return session.query(Message).filter_by(DEVICE_ID=device_id, MESSAGE_STATE_ID=1).first()
    except Exception as e:
        print(e)


def sqlite_get_processed_messages():
    try:
        return session.query(Message).filter(Message.MESSAGE_STATE_ID != 1).all()
    except Exception as e:
        print(e)


def sqlite_update_message(message):
    try:
        session.add(message)
        session.commit()
        return True
    except Exception as e:
        print(e)
