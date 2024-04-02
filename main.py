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

    @property
    def totp(self) -> TOTP:
        return self._totp

    @property
    def secret_key(self) -> str:
        return self._secret_key

    @staticmethod
    def _generate_secret_key() -> str:
        secret_bytes = secrets.token_bytes(20)
        secret_key = base64.b32encode(secret_bytes).decode('utf-8')
        return secret_key

    @staticmethod
    def get_or_create_secret_key(db, user_id: str) -> str:
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if db_user:
            return db_user.secret_key
        secret_key = TwoFactorAuth._generate_secret_key()
        db.add(User(user_id=user_id, secret_key=secret_key))
        db.commit()
        return secret_key        

    def _create_qr_code(self) -> bytes:
        uri = self.totp.provisioning_uri(
            name=self._user_id,
            issuer_name='2FA',
        )
        img = qrcode.make(uri)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        return img_byte_array.getvalue()  

    @property  
    def qr_code(self) -> bytes:
        if self._qr_cache is None:
            self._qr_cache = self._create_qr_code()
        return self._qr_cache

    def verify_totp_code(self, totp_code: str) -> bool:
        return self.totp.verify(totp_code)