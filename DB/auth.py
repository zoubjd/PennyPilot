#!/usr/bin/env python3
"""
Main file
"""
import bcrypt
import uuid
from DB.db import DB
from DB.tables import User
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> bytes:
    """hashes the password"""
    byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte, salt)


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Registers a User"""
        user = self._db._session.query(User).filter_by(email=email).first()
        if user:
            raise ValueError(f"User {email} already exists")
        else:
            hashed_password = _hash_password(password)
            user = self._db.add_user(email, hashed_password)
            self._db._session.add(user)
            self._db._session.commit()
            return user

    def valid_login(self, email: str, password: str) -> bool:
        """validates if the user exists and id the passwd is correct"""
        if email is None or password is None:
            return False
        user = self._db._session.query(User).filter_by(email=email).first()
        if user is None:
            return False
        hashed = user.hashed_password
        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            return True
        else:
            return False

    def _generate_uuid(self) -> str:
        """generate id using uuid"""
        return str(uuid.uuid4())

    def create_session(self, email: str) -> str:
        """generates a session_id if user exists"""
        if email is None:
            return None
        user = self._db._session.query(User).filter_by(email=email).first()
        if user is None:
            return None
        id = self._generate_uuid()
        user.session_id = id
        self._db._session.commit()
        return id

    def get_user_from_session_id(self, session_id: str) -> User:
        """gets the user based on the session id"""
        if session_id is None:
            return None
        user = self._db._session.query(
            User).filter_by(session_id=session_id).first()
        if user is None:
            return None

        return user

    def destroy_session(self, user_id: int) -> None:
        """destroys the session id based on a user id"""
        if user_id is None:
            return None
        user = self._db._session.query(User).filter_by(id=user_id).first()
        if user is None:
            return
        user.session_id = None
        self._db._session.commit()

    def get_reset_password_token(self, email: str) -> str:
        """generates a password reset token"""
        if email is None:
            return None
        user = self._db._session.query(User).filter_by(email=email).first()
        if user is None:
            raise ValueError()
        token = str(uuid.uuid4())
        user.reset_token = token
        self._db._session.commit()
        return token

    def update_password(self, reset_token: str, new_pwd: str) -> None:
        """updates the lost password"""
        if reset_token is None or new_pwd is None:
            raise ValueError()
        user = self._db._session.query(
            User).filter_by(reset_token=reset_token).first()
        if user is None:
            raise ValueError()
        new_hash = _hash_password(new_pwd)
        user.hashed_password = new_hash
        user.reset_token = None
        self._db._session.commit()
