from fastapi import FastAPI
from mtasks.routers import tasks, users

app = FastAPI()

# Подключаем маршруты

app.include_router(tasks.router)
app.include_router(users.router)

@app.get("/")
def root():
    """Главная страница"""
    return {"message": "Welcome to Task & User Manager App"}


"""
В файле main.py создайте сущность FastAPI(), напишите один маршрут для неё - '/', по которому функция возвращает 
словарь - {"message": "Welcome to Taskmanager"}. Импортируйте объекты APIRouter и подключите к ранее созданному 
приложению FastAPI, объединив все маршруты в одно приложение.
"""