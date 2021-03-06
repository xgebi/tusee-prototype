from datetime import datetime, timedelta
import uuid
from typing import Dict

import jwt
import psycopg
import pyotp
from argon2 import PasswordHasher
from flask import wrappers, current_app

from app import db
from app.exceptions import UserExistsException


def create_user(display_name: str, password: str, email: str, conn: psycopg.Connection) -> str:
    with conn.cursor() as cur:
        cur.execute("""SELECT user_uuid FROM tusee_users WHERE email = %s""", (email, ))
        user_exists = len(cur.fetchall()) > 0
        if user_exists:
            raise UserExistsException("User already exists")
        ph = PasswordHasher()
        now = datetime.now()
        user_uuid = str(uuid.uuid4())
        cur.execute("""INSERT INTO tusee_users (user_uuid, display_name, password, email, created, first_login, uses_totp, totp_secret) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_uuid, display_name, ph.hash(password), email, now, True, True,
                     pyotp.random_base32()))
    conn.commit()
    return user_uuid


def authenticate_user(request: wrappers.Request, connection: psycopg.Connection):
    auth = request.headers.get('authorization')
    decoded = jwt.decode(auth, current_app.config["SECRET_KEY"], algorithms="HS256")
    user = get_user_by_email(decoded["email"], conn=connection)
    if user:
        if user["expiry_date"] is not None and user["expiry_date"] > datetime.now().astimezone():
            expiry_time = (datetime.now() + timedelta(0, 0, 0, 0, 30)).astimezone().isoformat()
            user["expiry_date"] = expiry_time
            user["token"] = jwt.encode({"email": user["email"], "expiry_date": expiry_time},
                                       current_app.config["SECRET_KEY"], algorithm="HS256")
            update_user(conn=connection, user=user)
            return user
    return None


def get_user_by_email(email: str, conn: psycopg.Connection) -> Dict or None:
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute("""SELECT user_uuid, display_name, password, email, 
        created, first_login, uses_totp, totp_secret, expiry_date FROM tusee_users WHERE email = %s""", (email,))
        return cur.fetchone()


def update_user(user: Dict, conn: psycopg.Connection):
    with conn.cursor() as cur:
        cur.execute("""UPDATE tusee_users SET display_name = %s, password = %s, email = %s, 
        first_login = %s, uses_totp = %s, totp_secret = %s, expiry_date = %s WHERE user_uuid = %s""",
                    (user.get('display_name'), user.get('password'), user.get('email'),
                     user.get('first_login'), user.get('uses_totp'),
                     user.get('totp_secret'), user.get('expiry_date'),
                     user.get('user_uuid')))
    conn.commit()
