
from sqlalchemy import Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.orm import declarative_base, relationship
from typing import List

Base = declarative_base()
metadata = MetaData()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(255))
   
    tasks = relationship("Task", back_populates="user")

   

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")