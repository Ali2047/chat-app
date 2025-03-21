from fastapi import Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from . import database, crud, schemas, auth
from jose import JWTError, jwt

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Check if the Authorization header starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise credentials_exception
    # Extract the token by removing the "Bearer " prefix
    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user

def get_current_user_for_websocket(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    user = crud.get_user_by_id(db, int(user_id))
    return user