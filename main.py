import base64
import io
import secrets
from typing import Optional

import qrcode
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pyotp import TOTP 
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///./2fa.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True, index=True)
    secret_key = Column(String, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class TwoFactorAuth:
    def __init__(self, user_id: str, secret_key: str):
        self._user_id = user_id
        self._secret_key = secret_key
        self._totp = TOTP(self._secret_key)
        self._qr_cache: Optional[bytes] = None