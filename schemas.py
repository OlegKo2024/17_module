"""
Схемы:
Создайте 4 схемы в модуле schemas.py, наследуемые от BaseModel, для удобной работы с будущими объектами БД:

    CreateUser с атрибутами: username(str), firstname(str), lastname(str) и age(int)
    UpdateUser с атрибутами: firstname(str), lastname(str) и age(int)
    CreateTask с атрибутами: title(str), content(str), priority(int)
    UpdateTask с теми же атрибутами, что и CreateTask.

Обратите внимание, что 1/2 и 3/4 схемы обладают одинаковыми атрибутами.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int
    slug: str


class User(UserBase):
    user_id: int  # Было user_id, теперь id (как в модели SQLAlchemy) - все перевел на обратно

    class Config:
        from_attributes = True  # Было orm_mode=True (Pydantic v2)
# параметр from_attributes = True (ранее назывался orm_mode = True) позволяет Pydantic автоматически конвертировать
# SQLAlchemy/Django ORM-объекты в Pydantic-модели. Этот параметр позволяет Pydantic читать данные не только из словарей,
# но и из ORM-объектов (например, SQLAlchemy, Django ORM, TortoiseORM).
#   Допустим, у вас есть SQLAlchemy-модель. Если вы попытаетесь передать объект SQLTask в Pydantic-модель
# без from_attributes, получите ошибку: TypeError: "SQLTask" is not a dict.
# Если добавить Config. Теперь Pydantic сможет автоматически извлекать данные из ORM-объекта
#   from_attributes = True полезен, когда:
# Вы используете SQLAlchemy, Django ORM, TortoiseORM и хотите легко конвертировать ORM-объекты в Pydantic-модели.
# Вы возвращаете объекты из БД в FastAPI (иначе FastAPI не сможет автоматически сериализовать ORM-объект в JSON)
#   Если вы используете SQLAlchemy + FastAPI, эта настройка обязательна для корректной работы
#   ORM = Object-Relational Mapping (объектно-реляционное отображение).
# Это технология, которая позволяет работать с базой данных (например, PostgreSQL, MySQL) как с обычными объектами
# в коде на Python (или другом языке). Это экземпляр класса, который представляет запись в таблице БД

class CreateUser(UserBase):
    pass


class UpdateUser(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None
    slug: Optional[str] = None

# firstname: Optional[str] = None - это означает, что firstname может быть либо строкой, либо None, по умолчанию - None
# exclude_unset=True — это параметр метода model_dump(), который указывает Pydantic исключить из результата все поля,
# которые не были явно переданы в модель при создании
# Что лучше использовать?
# Если Swagger UI мешает (предзаполняет поля)
#   Способ 1 (рекомендуемый)
# Использовать exclude_unset=True.
# Вручную удалять неизменяемые поля из JSON в Swagger UI перед отправкой.
#   Способ 2 (альтернативный) - используемый
# Использовать exclude_unset=True, exclude_none=True.
# Вместо удаления поля ставить null (если None не является валидным значением)
#   Если можно настроить клиент (например, Postman или кастомный фронтенд)
# Лучше всего не отправлять неизменяемые поля вообще. Тогда exclude_unset=True будет работать идеально


class TaskBase(BaseModel):
    title: str
    content: str = Field(
        ...,
        max_length=100,
        min_length=5,
        description="Описание задачи"
    )
    priority: int = Field(
        0,
        ge=0,
        le=3
    )
    completed: bool = False
    slug: str
    user_id: int


class Task(TaskBase):
    task_id: int

    class Config:
        from_attributes = True


class CreateTask(TaskBase):
    pass


class UpdateTask(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = Field(
        None,
        max_length=100,
        min_length=5,
        description="Описание задачи"
    )
    priority: Optional[int] = Field(
        0,
        ge=0,
        le=3
    )
    completed: Optional[bool] = False
    slug: Optional[str] = None
    user_id: Optional[int] = None



