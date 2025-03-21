from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    messages = relationship("Message", back_populates="sender")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500))
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sender = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")  # Fixed back_populates