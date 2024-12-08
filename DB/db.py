#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Type, List
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4

from DB.tables import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        # Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database.
        Args:
            email (str): The user's email.
            hashed_password (str): The user's hashed password.

        Returns:
            User: The newly created User object.
        """
        # Create a new User instance
        userid = str(uuid4())
        new_user = User(email=email, hashed_password=hashed_password, id=userid)
        # Add and commit the new user to the database
        self._session.add(new_user)
        self._session.commit()
        # Return the created User instance
        return new_user

    def find_user_by(self, **kwargs: List[any]) -> User:
        """Find a user by arbitrary keyword arguments.
        Args:
            **kwargs: Arbitrary keyword arguments for filtering.

        Returns:
            User: The first User object that matches the criteria.

        Raises:
            NoResultFound: If no user matches the criteria.
            InvalidRequestError: If invalid filtering criteria are provided.
        """
        try:
            # Use SQLAlchemy's filter_by with **kwargs for dynamic filtering
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound("Not found")
            return user
        except InvalidRequestError as e:
            # Raised if invalid column names are used in kwargs
            raise InvalidRequestError("Invalid")

    def update_user(self, user_id: int, **kwargs: List[any]) -> None:
        """Updates the user based on the id and provided attributes.

        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Arbitrary keyword arguments representing
            attributes to update.

        Raises:
            NoResultFound: If no user with the given ID is found.
            ValueError: If any key in kwargs is not a valid user attribute.
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            raise NoResultFound()
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise ValueError()
        self._session.commit()
