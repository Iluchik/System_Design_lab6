from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from model.DBconfig import User_description, User, get_db, redis_client
import json

SECRET_KEY = "System-design-Lab2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 20

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==== User service ===================================================================================================

# Черный список токенов доступа
token_BL = []

class user_service():

	async def authentification(self, token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
		credentials_exception = HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
			headers={"WWW-Authenticate": "Bearer"}
		)
		try:
			if token in token_BL:
				raise credentials_exception
			payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
			email: str = payload.get("sub")
			user = db.query(User).filter(User.email == email).first()
			if user is None:
				raise credentials_exception
			return {"user": user, "token": token}
		except JWTError:
			raise credentials_exception

	def authorization(self, data: dict, expires_delta: Optional[timedelta] = None):
		payload = data.copy()
		if expires_delta:
			expire = datetime.utcnow() + expires_delta
		else:
			expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
		payload.update({"exp": expire})
		token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
		return token

	async def create_user(self, user: User_description, db: Session):
		user.password = pwd_context.hash(user.password)
		db_user = User(**user.dict())
		db.add(db_user)
		db.commit()
		db.refresh(db_user)
		return db_user

	async def login(self, form_data: OAuth2PasswordRequestForm, email: str, db: Session):
		user = db.query(User).filter(User.email == email).first()
		if user is None:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect email, username or password",
				headers={"WWW-Authenticate": "Bearer"}
			)
		if pwd_context.verify(form_data.password, user.password):
			expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
			access_token = self.authorization(data={"sub": email}, expires_delta=expire)
			return {"access_token": access_token, "token_type": "bearer"}
		else:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect email, username or password",
				headers={"WWW-Authenticate": "Bearer"}
			)

	async def get_users(self, db: Session):
		return db.query(User).all()

	async def get_user(self, user_id: int, db: Session):
		cache_key = f"user:{user_id}"
		if redis_client.exists(cache_key):
			cached_user = redis_client.get(cache_key)
			return json.loads(cached_user)
		else:
			user = db.query(User).filter(User.id == user_id).first()
			if user:
				user.__delattr__("_sa_instance_state")
				redis_client.set(cache_key, json.dumps(user.__dict__), ex=180)
			else:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
			return user.__dict__

	async def update_user(self, updated_user: User_description, current_user: dict, db: Session):
		cache_key = f"user:{current_user['user'].id}"
		if redis_client.exists(cache_key):
			user = dict(json.loads(redis_client.get(cache_key)))
			user = User(id=user["id"], first_name=user["first_name"], last_name=user["last_name"], email=user["email"], password=user["password"], age=user["age"], adress=user["adress"], phone=user["phone"])
		else:
			user = db.query(User).filter(User.id == current_user["user"].id).first()
			if user is None:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
		user.first_name = updated_user.first_name
		user.last_name = updated_user.last_name
		user.email = updated_user.email
		user.password = pwd_context.hash(updated_user.password)
		user.age = updated_user.age
		user.adress = updated_user.adress
		user.phone = updated_user.phone
		db.commit()
		redis_client.set(cache_key, json.dumps(dict(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password, age=user.age, adress=user.adress, phone=user.phone)), ex=180)
		return user

	async def delete_account(self, current_user: dict, db: Session):
		user = db.query(User).filter(User.id == current_user["user"].id).first()
		if user is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
		db.delete(user)
		db.commit()
		return user

	async def logout(self, current_user: dict, db: Session):
		cache_key = f"user:{current_user['user'].id}"
		if redis_client.exists(cache_key):
			user = dict(json.loads(redis_client.get(cache_key)))
		else:
			user = db.query(User).filter(User.id == current_user["user"].id).first()
			if user is None:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
		token_BL.append(current_user["token"])
		return user

# =====================================================================================================================