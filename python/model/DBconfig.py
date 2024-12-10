from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://cacheRedis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

DATABASE_URL_MONGO = os.getenv("MONGO_URL", "mongodb://mongoDB:27017/")
client = MongoClient(DATABASE_URL_MONGO)
archdb = client["arch"]
package_collection = archdb["packages"]

DATABASE_URL_POSTGRES = os.getenv("DATABASE_URL", "postgresql://stud:stud@postgreDB/arch")
engine = create_engine(DATABASE_URL_POSTGRES)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
		db = SessionLocal()
		try:
			yield db
		finally:
			db.close()

# ==== Models =========================================================================================================

# ---- User -----------------------------------------------------------------------------------------------------------
class User_description(BaseModel):
	first_name: str
	last_name: str
	email: str
	password: str
	age: Optional[int] = None
	adress: Optional[str] = None
	phone: Optional[str] = None

class User(Base): # Это класс SQLAlchemy, тут используется Base, А НЕ BaseModel!!!
	__tablename__ = "users"
	id = Column(Integer, primary_key=True)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String, unique=True)
	password = Column(String)
	age = Column(String, nullable=True)
	adress = Column(String, nullable=True)
	phone = Column(String, nullable=True)
	idx = Index("user_idx", id, email)

class User_response(User_description):
	id: int
	class Config:
		orm_mode=True
# ---------------------------------------------------------------------------------------------------------------------

# ---- Package --------------------------------------------------------------------------------------------------------
class Package_description(BaseModel):
	recipient_id: int
	package_details: dict

class Package(Package_description):
	_id: str
	sender_id: int
# ---------------------------------------------------------------------------------------------------------------------
	
# =====================================================================================================================

Base.metadata.create_all(bind=engine)