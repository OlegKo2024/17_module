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

# from mtasks.models import User_sql  # SQLAlchemy in addition
# Роутеры должны зависеть от схем (Pydantic), а не от моделей SQLAlchemy
# FastAPI работает с response_model и валидацией через Pydantic (User, CreateUser и т. д.), а не напрямую с SQLAlchemy.
# Всё взаимодействие с БД должно происходить в services или crud-слое, а не в роутерах.

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

# список словарей
# Сравнение users: list[User] = [] с users = []:
# Запись users = [] создаёт пустой список без указания типа элементов.
# Это более гибкий подход, но он не даёт подсказок о том, какие данные должны храниться в списке.
# users: list[User] = [] - будет предупреждение, так как здесь users это список объектов

users = []  # Список пользователей (храним словари)


@router.get("/", response_model=list[User])
async def get_all_users():
    return [User(**u) for u in users]  # Преобразование каждого словаря в объект User
    # return users - не правильно, так как response_model=list[User] - список объектов, а не словарей

#   1. Если используете response_model=list[User], функция должна возвращать список объектов User, а не список словарей.
# Преобразование словарей в объекты User с помощью [User(**u) for u in users] ГАРАНТИРУЕТ, что данные соответствуют
# модели и ожиданиям FastAPI.
# response_model=list[User] указывает FastAPI, что эндпоинт возвращает список объектов User.
# User(**user) — это распаковка словаря в атрибуты модели Pydantic (эквивалентно User(id=1, name="Alice")).
# FastAPI автоматически сериализует объекты User в JSON, используя их схему. Когда FastAPI говорит, что он сериализует
# объекты в JSON, это означает, что он преобразует ваши данные (например, экземпляры Pydantic-моделей, словари, списки)
# в строку JSON, которую можно отправить по HTTP

#   2. Можно просто вернуть список словарей (FastAPI автоматически проверит их на соответствие response_model
# (проверяет, в словарях есть все поля из User с правильными типами))
# return users - работает, но без явного преобразования в User. FastAPI автоматически проверит, что
# структура словарей соответствует модели User. Модель» — это Pydantic-модель из модуля schemas (например, User),
# а не модель базы данных (например, SQLAlchemy UserDB)
# Ограничения: Если в users есть лишние поля, которых нет в User, они будут отброшены и Если каких-то полей не хватает
# или типы не совпадают — FastAPI вызовет ошибку валидации (422 Unprocessable Entity)

#   3. Если убрать response_model. Можно вообще не указывать response_model и вернуть users как есть:
# FastAPI не будет проверять структуру данных.
# В Swagger/OpenAPI не будет информации о формате ответа (документация ухудшится).
# Риск: если в словарях есть несериализуемые объекты (например, datetime), FastAPI может упасть с ошибкой.

#   4. Использовать response_model=list[dict]
# Если явно указать, что возвращаете список словарей, но БЕЗ привязки к модели:
# Плюсы:
# FastAPI гарантирует, что это будет список (но не проверяет содержимое словарей).
# Swagger отобразит примерный формат ответа (но без деталей полей, как в User).
# Минусы:
# Нет валидации/автодокументации структуры словарей.
# Риск отправить клиенту "мусорные" данные.


@router.get("/{slug}", response_model=User)
def get_user_by_id(slug: str):
    for u in users:
        if u['slug'] == slug:
            return User(**u)
            # return u  - не правильно, так как response_model=User - объект
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.post("/create", response_model=User)  # FastAPI ожидает, что функция вернёт объект типа User
def create_user(user: CreateUser):
    if any(user.username == u['username'] for u in users):
        raise HTTPException(status_code=400, detail="User already exists")
    if any(u["slug"] == user.slug for u in users):
        raise HTTPException(status_code=400, detail="Slug already exists")
    new_id = max((u['user_id'] for u in users), default=0) + 1
    new_user = {
        "user_id": new_id,
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "age": user.age,
        "slug": user.slug
    }
    users.append(new_user)
    return User(**new_user)  # Преобразование словаря в объект User
# В этом варианте мы возвращаем словарь, но преобразуем его в объект User с помощью User(**new_user)
# return new_user - это не правильно, так как response_model=User - объект, а не словарь

#   Почему предупреждение ушло:
# Когда вы изменили users: list[User] = [] на users = [], анализатор кода перестал проверять типы элементов списка users
# Однако, чтобы соответствовать response_model=User, всё равно нужно преобразовать словарь в объект User перед возвратом

# Обратный слэш позволяет переносить строки, но его лучше не использовать, может привести к ошибке, если пробел
# То есть лучший вариант, как показано выше и ниже с использованием скобок (), [], {} для переноса - наиболее читаемый
#    message = (
#         f"Hello, {user_name}. "
#         f"Your account balance is {balance:.2f}. "
#         f"Last login: {last_login}"
#     )


""" НИЖЕ PUT и PATCH работают одинаково (как частичное обновление), но это антипаттерн.
Исправьте PUT для полной замены ресурса либо удалите его, оставив только PATCH.
URL (/{username}) у вас теперь правильный для обоих методов. """

@router.put("/{username}", response_model=User)     # изменил update на {username}, см. ниже
def update_user(username: str, user: UpdateUser):  # сделал изменение на username, а не user_id
    for u in users:
        if u['username'] == username:
            if user.firstname is not None:  # проверяю, что поле firstname в объекте UpdateUser не равно None.
                # Это важно, потому что Pydantic-модель UpdateUser может содержать None
                # для необязательных полей (если они помечены как Optional)
                u['firstname'] = user.firstname # Если поле передано (не None), вы обновляете соответствующий ключ
                # в словаре u. Это стандартный подход для частичного обновления данных.
            if user.lastname is not None:
                u['lastname'] = user.lastname
            if user.age is not None:
                u['age'] = user.age
            if user.slug is not None:
                u["slug"] = user.slug
            return User(**u)
            # return u  - не правильно, так как response_model=User - объект
    raise HTTPException(status_code=404, detail="Product not found")

# Поведение PUT с Optional-полями
# Если в модели Pydantic поля помечены как Optional, и клиент отправляет не все поля в PUT-запросе, то:
# Сервер получит None для непереданных полей (если они не заданы в запросе). Ваша текущая логика (if field is not None)
# сохранит прежние значения, но это нестандартно для PUT. По REST-стандарту PUT должен заменить весь ресурс!
# Если поле не передано, оно должно стать null и для частичного обновления лучше использовать Patch.


#   Вариант 1 (С next() + model_dump):
# Использует next() для поиска пользователя (более лаконично, но менее явно).
# model_dump() — метод Pydantic v2 (актуально для Python 3.10+).
# Постепенное обновление полей через цикл
@router.patch("/one/{username}", response_model=User)
def update_user_patch_one(username: str, user: UpdateUser):
    user_data = next((u for u in users if u['username'] == username), None)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    updates = user.model_dump(exclude_unset=True, exclude_none=True)  # Pydantic v2
    for field, value in updates.items():
        user_data[field] = value        # user_data.update(updates) - иной вариант
    return User(**user_data)

# Почему exclude_defaults не сработал?
# exclude_defaults исключает только поля, которые равны default-значениям модели.
# В вашей модели все default-значения — None, а клиент присылает "string"/0 (не None), поэтому они не исключаются.
# exclude_unset vs exclude_defaults
# Параметр	Поведение	Когда использовать
# exclude_unset=True	Исключает поля, не переданные в запросе (но включает null).	Если клиент отправляет только изменяемые поля.
# exclude_defaults=True	Исключает поля, равные дефолтным значениям модели (например, None).	Если клиент может присылать все поля, включая "пустые".

#   Вариант 1 (С next() + model_dump) улучшенный:
@router.patch("/two/{username}", response_model=User)
def update_user_patch_two(username: str, user: UpdateUser):
    user_data = next((u for u in users if u['username'] == username), None) # Ссылка на словарь user из списка users (если найден).
# def next(*args, **kwargs) - **kwargs это default, можно записать
# (u for u in users if u['username'] == username) - это генераторное выражение, которое создаёт итератор
# next() пытается получить первый элемент из этого итератора, если совпадение не найдено (итератор пуст), возврат None
# Когда использовать next()
    # Когда нужно получить только первый элемент, удовлетворяющий условию - наш случай
    # При работе с большими данными, которые не нужно хранить в памяти целиком
    # Для извлечения элементов из итераторов вручную
# Пример альтернативы:
    # Вместо: first_match = next((x for x in items if condition(x)), None)
    # Можно:
    # first_match = None
    # for x in items:
    #     if condition(x):
    #         first_match = x
    #         break
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user_data.update(user.model_dump(exclude_unset=True, exclude_none=True))   # user - объект Pydantic модели UpdateUser, содержит новые данные
    # user.model_dump(exclude_unset=True): - преобразует модель в словарь
    # exclude_unset=True означает, что в словарь попадут только те поля, которые были явно заданы в запросе
    # user_data.update() обновляет исходный словарь пользователя новыми значениями
    # model_dump() в Pydantic преобразует объект модели в обычный Python-словарь
    # class User(BaseModel):
    #     name: str
    #     age: int
    # user = User(name="Alice", age=25)
    # user_dict = user.model_dump()
    # # Результат: {'name': 'Alice', 'age': 25}
    return User(**user_data)

# Для PATCH клиент передаёт только изменяемые поля, а сервер обновляет только их.
# В модели Pydantic все поля должны быть Optional, но в роутинге указываются все возможные поля, которые можно изменить

# Вариант 2 (Цикл + dict() + update):
# Классический подход с явным циклом.
# dict(exclude_unset=True) — устаревший метод в Pydantic v2 (лучше заменить dict на model_dump - заменил).
# Обновление словаря целиком через update().


@router.patch("/three/{username}", response_model=User)
def update_user_patch_three(username: str, user: UpdateUser):
    for u in users:
        if u['username'] == username:
            updates = user.dict(exclude_unset=True, exclude_none=True)  # Только переданные поля
            u.update(updates)
            return User(**u)
    raise HTTPException(status_code=404, detail="User not found")


# Вариант 3 (Ручные проверки is not None):
@router.patch("/plus/{username}", response_model=User)
async def update_user_patch_plus(username: str, user: UpdateUser):
    for u in users:
        if u['username'] == username:
            if user.firstname is not None:
                u['firstname'] = user.firstname
            if user.lastname is not None:
                u['lastname'] = user.lastname
            if user.age is not None:
                u['age'] = user.age
            if user.slug is not None:
                u["slug"] = user.slug
            return User(**u)
    raise HTTPException(status_code=404, detail="Задача не найдена")

#   Что правильно: PUT /update и PATCH /{username} или PUT /{username} и PATCH /{username}
# Правильнее выбирать PUT /{username} и PATCH /{username} (унифицированные пути). Вот почему:
# 1. REST-стандарты и читаемость. Единый стиль URL:
# REST (Representational State Transfer) — это архитектурный стиль проектирования веб-сервисов, на стандартах HTTP.
# Он определяет набор принципов, по которым клиент и сервер должны обмениваться данными.
# В RESTful API путь /resource/{id} — стандарт для операций с конкретным ресурсом. Пример:
# GET /users/{username} — получить пользователя.
# PUT /users/{username} — полностью обновить.
# PATCH /users/{username} — частично обновить.
# DELETE /users/{username} — удалить.
# Вариант /update нарушает эту логику, добавляя глагол (update) в URL, что не рекомендуется.
# Почему /update — не идеально?
# Избыточно: HTTP-метод (PUT/PATCH) уже указывает на действие.
# Усложняет масштабирование: если позже добавите другие действия (например, /activate), API станет неконсистентным.


@router.delete("/delete", response_model=dict)
def delete_user(username: str):
    global users
    for u in users:
        if u['username'] == username:
            users = [u for u in users if u['username'] != username] # перезапись списка словарей без удаленного словаря
            return {"message": f"User: {username} deleted"}
    raise HTTPException(status_code=404, detail="User not found")

"""
    Почему работает username: str без Query?
@router.delete("/delete", response_model=dict)
def delete_user(username: str):  # Почему это работает без Query?
    ...

Причина: FastAPI автоматически интерпретирует параметры функции, которые:
Не указаны в пути (/delete/{username} → username был бы path-параметром).
Не являются телами запроса (т.е. не Request или Pydantic-моделью).
Как query-параметры! То есть FastAPI неявно преобразует username: str в username: str = Query(...).

    Аналогия с явным Query
Ваш код эквивалентен:

    from fastapi import Query

    @router.delete("/delete")
    def delete_user(username: str = Query(...)):  # Явное указание Query
    ...

    Когда нужно явно указывать Query?
Явное указание Query требуется, если нужно:
    Добавить описание (title, description).
    Указать дефолтное значение.
    Добавить валидацию (например, min_length, regex).
    
    from fastapi import Query

    @router.delete("/delete")
    def delete_user(
        username: str = Query(..., min_length=3, title="Username to delete")
    ):
    ...

"""