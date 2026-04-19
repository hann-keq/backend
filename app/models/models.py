
from sqlalchemy import Column, Integer, String, ForeignKey, MetaData,Enum
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
    phone_number = Column(String(20), nullable=True)
    tasks = relationship("Task", back_populates="user")
    pets = relationship("Pet", back_populates="user")

   
class Pet(Base):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(50))
    type = Enum('dog', 'cat',name='pet_type')
    breed = Column(String(50))
    age = Column(Integer)
    weight = Column(Integer)
    user = relationship("User", back_populates="pets")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")