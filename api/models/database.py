from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
from sqlalchemy.sql import func

Base = declarative_base()

class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    website = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    animals = relationship("Animal", back_populates="shelter")

class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    gender = Column(String)
    age = Column(String)
    birth_date = Column(DateTime) 
    description = Column(Text)
    image_url = Column(String)
    source_url = Column(String)
    is_adopted = Column(Boolean, default=False)
    shelter_id = Column(Integer, ForeignKey("shelters.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    shelter = relationship("Shelter", back_populates="animals")
    adoption_requests = relationship("AdoptionRequest", back_populates="animal")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    city = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    adoption_requests = relationship("AdoptionRequest", back_populates="user")

class AdoptionRequest(Base):
    __tablename__ = "adoption_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)
    request_date = Column(DateTime(timezone=True), server_default=func.now())
    
    animal = relationship("Animal", back_populates="adoption_requests")
    user = relationship("User", back_populates="adoption_requests")

