from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_name = Column(String, unique=True, nullable=False)
    periodicity = Column(String, nullable=False)
    on_going = Column(Boolean, default=True)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
