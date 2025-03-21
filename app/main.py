from fastapi import FastAPI, Depends, HTTPException, WebSocket, Query
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth, database, dependencies, websocket
from .database import engine, SessionLocal
from .websocket import manager
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db, user)
    return db_user

@app.post("/api/login")
def login(login_request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, login_request.username, login_request.password)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

@app.post("/api/logout")
def logout():
    # In a real app, you might blacklist the token here
    return {"message": "Logout successful"}

@app.get("/api/chat/rooms", response_model=list[schemas.Room])
def get_rooms(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(dependencies.get_current_user)):
    return crud.get_rooms(db)

@app.get("/api/chat/rooms/{room_id}", response_model=schemas.Room)
def get_room(room_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(dependencies.get_current_user)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    user_ids = manager.get_users_in_room(room_id)
    room.users = [crud.get_user_by_id(db, user_id) for user_id in user_ids if crud.get_user_by_id(db, user_id)]
    return room

@app.post("/api/chat/rooms/{room_id}/messages", response_model=schemas.Message)
async def create_message(
    room_id: int,
    message: schemas.MessageCreate,
    current_user: schemas.User = Depends(dependencies.get_current_user),
    db: Session = Depends(database.get_db)
):
    msg = crud.create_room_message(db, message, current_user.id, room_id)
    await manager.broadcast(f"User {current_user.id}: {message.text}", room_id)
    return msg

@app.get("/api/chat/rooms/{room_id}/messages", response_model=list[schemas.Message])
def get_messages(room_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(dependencies.get_current_user)):
    return crud.get_room_messages(db, room_id)

@app.get("/api/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(dependencies.get_current_user)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str = Query(...), db: Session = Depends(database.get_db)):
    user = dependencies.get_current_user_for_websocket(token, db)
    if user is None:
        await websocket.close(code=1008)  # Policy violation (invalid token)
        return
    await manager.connect(websocket, room_id, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room_id)
    except:
        manager.disconnect(websocket, room_id, user.id)

@app.on_event("startup")
def startup_event():
    # Create a new session directly instead of using the dependency
    db = SessionLocal()
    try:
        if not crud.get_rooms(db):
            crud.create_room(db, schemas.RoomCreate(name="General"))
        db.commit()
    finally:
        db.close()