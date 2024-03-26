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
