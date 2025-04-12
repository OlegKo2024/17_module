"""
В модуле task.py создайте модель Task, наследованную от ранее написанного Base со следующими атрибутами:

    __tablename__ = 'tasks'
    id - целое число, первичный ключ, с индексом.
    title - строка.
    content - строка.
    priority - целое число, по умолчанию 0.
    completed - булевое значение, по умолчанию False.
    user_id - целое число, внешний ключ на id из таблицы 'users', не NULL, с индексом.
    slug - строка, уникальная, с индексом.
    user - объект связи с таблицей User, где back_populates='tasks'.

"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from mtasks.backend.db import Base   # относительный от родительского пакета
# Если нужен импорт из текущего пакета – используйте одну точку (.). Если из родительского – две точки (..).
from sqlalchemy.orm import relationship


class Task(Base):
    __tablename__ = 'tasks'
    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    priority = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)  # Связь с User
    slug = Column(String, unique=True, index=True)
    user = relationship('User', back_populates='tasks') # ссылка на user

#   ForeignKey("users.id")
# Создает внешний ключ (FOREIGN KEY), ссылающийся на столбец id в таблице users.
# Гарантирует целостность данных: нельзя вставить user_id, которого нет в users.id

# Неявный nullable=False
# По умолчанию Column имеет nullable=True, но для внешних ключей (ForeignKey) часто подразумевается NOT NULL.
# Если нужно явно запретить NULL: user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

#   В SQLAlchemy, user в строке user = relationship('User', back_populates='tasks') — ссылка на объект класса User
# user — это атрибут, который создается в классе, где определена эта строка (например, в классе Task).
# Этот атрибут представляет собой ссылку на объект класса User, связанный с текущим объектом
# (например, с объектом Task). См ниже.

"""
Ссылка в индексе — это указатель на физическое расположение строки в таблице. В большинстве случаев это не ID строки, 
а внутренний идентификатор, который база данных использует для быстрого доступа к данным. Однако в некоторых базах 
данных (например, SQLite) ссылка может совпадать с ROWID или первичным ключом (id), если он есть

Индекс — это отдельная структура данных, которая хранится независимо от основной таблицы. Это не обязательно таблица в
привычном смысле, а скорее оптимизированная для поиска структура

Как работает поиск по индексу?
Давайте разберем ваш пример:

Таблица users:
id	name	email
1	Alice	alice@example.com
2	Bob	    bob@example.com
3	Charlie	charlie@example.com
Индекс для колонки name:
Значение (name)	Ссылка на строку
Alice	1
Bob	    2
Charlie	3

Запрос:
SELECT * FROM users WHERE name = 'Alice';

Шаги поиска:
Поиск в индексе:
    База данных ищет значение 'Alice' в индексе (в колонке Значение (name)).
    Поскольку индекс отсортирован (например, это B-дерево), поиск происходит быстро.
Получение ссылки:
    В индексе для 'Alice' указана ссылка 1.
Переход к данным в таблице:
    База данных использует ссылку 1, чтобы найти строку в таблице users.
В таблице users строка с id = 1 содержит данные:
    id: 1, name: Alice, email: alice@example.com
База данных возвращает строку:
(1, 'Alice', 'alice@example.com')

    Что такое users и id в user_id = Column(Integer, ForeignKey("users.id")) ?
users — это имя таблицы в базе данных, которая хранит категории.
id — это первичный ключ (primary key) таблицы categories. Он уникально идентифицирует каждую запись в таблице.
    Что делает ForeignKey?
ForeignKey("users.id") указывает, что колонка user_id в таблице tasks ссылается на колонку id в таблице
users. Это создает внешний ключ (foreign key), который обеспечивает связь между таблицами.

    slug = Column(String, unique=True, index=True)
slug — это колонка в таблице базы данных, которая хранит строковые данные (тип String).
Технически:
В базе данных это будет колонка с именем slug, которая хранит строки.
В Python-коде slug — это атрибут объекта, который представляет собой значение этой колонки.
Пример:
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, index=True)  # Колонка в таблице
Если вы создаете объект Task: task = Task(slug="buy-groceries")
То task.slug будет строкой "buy-groceries"

    user = relationship('User', back_populates='tasks')
user — это отношение (relationship), которое связывает текущий объект (Task) с объектом другого класса (User).
Технически:
В базе данных это реализуется через внешний ключ (foreign key), например, user_id, который ссылается на таблицу users.
В Python-коде user — это атрибут объекта, который представляет собой ссылку на связанный объект класса User.

"""