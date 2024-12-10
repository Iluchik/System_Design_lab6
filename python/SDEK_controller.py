from fastapi import FastAPI, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlalchemy.orm import Session
from services.user_service import user_service
from services.package_service import package_service
from model.DBconfig import User_description, User_response, get_db, Package_description

SECRET_KEY = "System-design-Lab2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 20

app = FastAPI()
user_service = user_service()
package_service = package_service()

# ==== User service ===================================================================================================

@app.post("/users", response_model=User_response)
async def create_user(user: User_description, db: Session = Depends(get_db), tags=["users"]):
	try:
		response: User_response = await user_service.create_user(user=user, db=db)
		return response
	except Exception as e:
		raise e

@app.post("/token", response_model=dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), email: str = Form(...), db: Session = Depends(get_db)):
	try:
		response: dict[str, str] = await user_service.login(form_data=form_data, email=email, db=db)
		return response
	except Exception as e:
		raise e

@app.get("/users", response_model=List[User_response], tags=["users"])
async def get_users(current_user: dict = Depends(user_service.authentification), db:Session = Depends(get_db)):
	try:
		response: List[User_response] = await user_service.get_users(db=db)
		return response
	except Exception as e:
		raise e

@app.get("/users/{user_id}", response_model=User_response, tags=["users"])
async def get_client(user_id: int, current_user: dict = Depends(user_service.authentification), db:Session = Depends(get_db)):
	try:
		response: User_response = await user_service.get_user(user_id=user_id, db=db)
		return response
	except Exception as e:
		raise e

@app.put("/users", response_model=User_response)
async def update_client(updated_user: User_description, current_user: dict = Depends(user_service.authentification), db:Session = Depends(get_db), tags=["users"]):
	try:
		response: User_response = await user_service.update_user(updated_user=updated_user, current_user=current_user, db=db)
		return response
	except Exception as e:
		raise e

@app.delete("/users/delete", response_model=User_response, tags=["users"])
async def delete_account(current_user: dict = Depends(user_service.authentification), db:Session = Depends(get_db)):
	try:
		response: User_response = await user_service.delete_account(current_user=current_user, db=db)
		return response
	except Exception as e:
		raise e

@app.delete("/users", response_model=User_response, tags=["users"])
async def logout(current_user: dict = Depends(user_service.authentification), db:Session = Depends(get_db)):
	try:
		response: User_response = await user_service.logout(current_user=current_user, db=db)
		return response
	except Exception as e:
		raise e

# =====================================================================================================================

# ==== Package service ================================================================================================

@app.post("/package")
async def create_package(package_desc: Package_description, current_user: dict = Depends(user_service.authentification)):
	try:
		response = await package_service.create_package(package_desc=package_desc, current_user=current_user)
		return response
	except Exception as e:
		raise e

@app.get("/package")
async def get_user_packages(current_user: dict = Depends(user_service.authentification)):
	try:
		response = await package_service.get_user_packages(current_user=current_user)
		return response
	except Exception as e:
		raise e

@app.put("/package")
async def update_package(updated_package: dict, current_user: dict = Depends(user_service.authentification)):
	try:
		response = await package_service.update_package(updated_package=updated_package, current_user=current_user)
		return response
	except Exception as e:
		raise e


@app.delete("/package/{product_id}")
async def delete_package(product_id: str, current_user: dict = Depends(user_service.authentification)):
	try:
		response = await package_service.delete_package(product_id=product_id, current_user=current_user)
		return response
	except Exception as e:
		raise e

# =====================================================================================================================

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)