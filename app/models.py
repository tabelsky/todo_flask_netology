import datetime
import uuid
from typing import List, Type

from config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, create_engine, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "todo_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan"
    )
    todos: Mapped[List["Todo"]] = relationship(
        "Todo", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "todos": [todo.id for todo in self.todos],
        }


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(
        UUID, server_default=func.gen_random_uuid(), unique=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("todo_user.id"))
    user: Mapped[User] = relationship(User, back_populates="tokens")

    @property
    def dict(self):
        return {"id": self.id, "token": self.token, "user_id": self.user_id}


class Todo(Base):
    __tablename__ = "todo"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    important: Mapped[bool] = mapped_column(Boolean, default=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    finish_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("todo_user.id"))
    user: Mapped[User] = relationship(User, back_populates="todos")

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "important": self.important,
            "done": self.done,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "finish_time": self.finish_time.isoformat() if self.finish_time else None,
            "user_id": self.user_id,
        }


MODEL_TYPE = Type[User | Token | Todo]
MODEL = User | Token | Todo

Base.metadata.create_all(bind=engine)
