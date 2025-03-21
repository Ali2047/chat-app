from sqlalchemy.orm import Session
from . import models, schemas, auth
from fastapi import HTTPException

def create_user(db: Session, user: schemas.UserCreate):
    # Check for duplicate username
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_rooms(db: Session):
    return db.query(models.Room).all()

def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def create_room_message(db: Session, message: schemas.MessageCreate, sender_id: int, room_id: int):
    db_message = models.Message(**message.dict(), sender_id=sender_id, room_id=room_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_room_messages(db: Session, room_id: int):
    return db.query(models.Message).filter(models.Message.room_id == room_id).all()