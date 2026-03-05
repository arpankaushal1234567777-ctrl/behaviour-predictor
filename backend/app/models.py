from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    logs = relationship("DailyLog", back_populates="owner")


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)

    sleep_hours = Column(Float)
    study_hours = Column(Float)
    screen_time = Column(Float)
    exercise_minutes = Column(Float)
    mood = Column(Integer)
    productivity_score = Column(Float)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="logs")