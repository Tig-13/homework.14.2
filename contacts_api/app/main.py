from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta
import os
import cloudinary
import cloudinary.uploader
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS
origins = ["http://localhost", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register/", response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = crud.create_user(db=db, user=user)
    token = crud.create_access_token(data={"sub": new_user.email})
    crud.send_verification_email(new_user.email, token)
    return new_user

@app.get("/verify-email/")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = crud.decode_token(token)  # используйте JWT decode для извлечения email
    user = crud.verify_user_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    return {"msg": "Email verified successfully"}

@app.post("/upload-avatar/")
def upload_avatar(file: UploadFile, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = cloudinary.uploader.upload(file.file)
    current_user.avatar_url = result['url']
    db.commit()
    return {"avatar_url": current_user.avatar_url}
