"""
В модуле user.py напишите APIRouter с префиксом '/user' и тегом 'user', а также следующие маршруты, с пустыми функциями:
    get '/' с функцией all_users.
    get '/user_id' с функцией user_by_id.
    post '/create' с функцией create_user.
    put '/update' с функцией update_user.
    delete '/delete' с функцией delete_user.
"""
from fastapi import APIRouter, HTTPException
from mtasks.schemas import User, CreateUser, UpdateUser

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

# список словарей
# Сравнение users: list[User] = [] с users = []:
# Запись users = [] создаёт пустой список без указания типа элементов.
# Это более гибкий подход, но он не даёт подсказок о том, какие данные должны храниться в списке.
users = []


@router.get("/", response_model=list[User])
async def get_all_users():
    return users


@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int):
    for u in users:
        if u['user_id'] == user_id:
            return u
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.post("/create", response_model=User)
def create_user(user: CreateUser):
    if any(user.username == u['username'] for u in users):
        raise HTTPException(status_code=400, detail="User already exists")
    new_id = max((u['user_id'] for u in users), default=0) + 1
    new_user = {
        "user_id": new_id,
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "age": user.age
    }
    users.append(new_user)
    return new_user
# Обратный слэш позволяет переносить строки, но его лучше не использовать, может привести к ошибке, если пробел
# То есть лучший вариант, как показано выше и ниже с использованием скобок (), [], {} для переноса - наиболее читаемый
#    message = (
#         f"Hello, {user_name}. "
#         f"Your account balance is {balance:.2f}. "
#         f"Last login: {last_login}"
#     )

@router.put("/update", response_model=User)
def update_user(username: str, user: UpdateUser):   # сделал изменение на username, а не user_id
    for u in users:
        if u['username'] == username:
            u['firstname'] = user.firstname
            u['lastname'] = user.lastname
            u['age'] = user.age
            return u
    raise HTTPException(status_code=404, detail="Product not found")


@router.delete("/delete", response_model=dict)
def delete_user(username: str):
    global users
    for u in users:
        if u['username'] == username:
            users = [u for u in users if u['username'] != username]
            return {"message": f"User: {username} deleted"}
    raise HTTPException(status_code=404, detail="User not found")