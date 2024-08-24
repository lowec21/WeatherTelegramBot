import datetime

from sqlalchemy import Integer, String, func

from database.database import engine
from .meta import Base
from sqlalchemy.orm import Mapped, mapped_column


class UserQueryHistory(Base):
    __tablename__ = 'user_query_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    user_query: Mapped[str] = mapped_column(String())
    timestamp: Mapped[datetime.datetime] = mapped_column(default=func.now())


class UserCity(Base):
    __tablename__ = 'user_city'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    current_user_city: Mapped[str | None] = mapped_column(String())


Base.metadata.create_all(engine)
