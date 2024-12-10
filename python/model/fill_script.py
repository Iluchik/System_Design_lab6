import pandas as pd
from sqlalchemy import create_engine
from DBconfig import Base, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine("postgresql+psycopg2://stud:stud@postgreDB/archdb")
Base.metadata.create_all(bind=engine)

data = {
	"first_name": ["Ivan", "Petr", "User"],
	"last_name": ["Ivanov", "Petrov", "Useov"],
	"email": ["ii@email.com", "pp@yandex.ru", "uu@umail.use"],
	"password": [f"{pwd_context.hash('qwerty')}", f"{pwd_context.hash('ytrewq')}", f"{pwd_context.hash('userty')}"],
	"age": ["22", "44", None],
	"adress": ["Moscow", "notMoscow", None],
	"phone": [None, None, "+7 (777) 777-77-77"]
}
df = pd.DataFrame(data)
df.to_sql("users", con=engine, if_exists = "append", index=False)