import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(f'sqlite:///{os.getcwd()}/messages.db', echo=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)


class MessageModel(Base):
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


Base.metadata.create_all(engine)
