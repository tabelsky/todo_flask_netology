import uuid
import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, create_session
from sqlalchemy import ForeignKey, String, UUID, Boolean, DateTime, func

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD


engine = create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)
Session = create_session(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'todo_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    tokens: Mapped[List['Token']] = relationship('Token', back_populates='user')
    todos: Mapped[List['Todo']] = relationship('Todo', back_populates='user')


class Token(Base):

    __tablename__ = 'token'
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('todo_user.id', ondelete='CASCADE'))
    user: Mapped[User] = relationship(User, back_populates='tokens')


class Todo(Base):

    __tablename__ = 'todo'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    important: Mapped[bool] = mapped_column(Boolean, default=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    finish_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('todo_user.id', ondelete='CASCADE'))
    user: Mapped[User] = relationship(User, back_populates='todos')


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

