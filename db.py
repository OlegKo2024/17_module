from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Импорт моделей (чтобы они зарегистрировались в Base.metadata)
# from mtasks.models import User_sql, Task_sql  # Абсолютный импорт (т.к. models/ — другой пакет) - вернул в create_db

DATABASE_URL = "sqlite:///mtasks/backend/taskmanager.db"    # Правильный путь
# Строка подключения sqlite:///.taskmanager.db преобразуется в абсолютный путь:
# D:\PythonProjectUni\Module_17_Resources\taskmanager.db
# Почему DATABASE_URL = "sqlite:///mtasks/backend/taskmanager.db" правильно (без точки):
# Текущая директория: D:\PythonProjectUni\Module_17_Resources\ (где запускаем python -m mtasks.backend.create_db)
# Путь интерпретируется как: D:\PythonProjectUni\Module_17_Resources\mtasks\backend\taskmanager.db
# Если добавить точку - создаст некорректный путь: D:\PythonProjectUni\Module_17_Resources\.mtasks\... (с лишней точкой)

# 3. Путь к SQLite (DATABASE_URL)
# Варианты:
# Путь	                                    Описание	                                                        Когда использовать
# sqlite:///taskmanager.db	                Создаётся в текущей рабочей директории (где запущен скрипт).	    Если БД должна быть в корне проекта.
# sqlite:///mtasks/backend/taskmanager.db	Жёстко заданный относительный путь внутри пакета.	                Если БД должна лежать в backend/.
# sqlite:///.taskmanager.db	                Точка в начале означает текущую директорию (аналог первго варианта)	Альтернатива sqlite:///taskmanager.db.


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)
# echo=True выводит SQL-запросы в консоль

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# sqlite: — это схема URI (в SQLite схема URI — это способ подключения к базе данных с использованием URI-формата
# (Uniform Resource Identifier), которая указывает на использование SQLite в качестве СУБД.
# Двоеточие (:) здесь разделяет схему (протокол) и остальную часть URI.
# /// — это разделитель, который указывает на начало пути к файлу базы данных. Три слэша (///) используются для
# обозначения относительного пути. В URI два слэша (//) обычно указывают на начало authority-части (например,
# имя хоста), но в случае SQLite они опускаются, и три слэша (///) сразу указывают на путь
# . — указывает на то, что путь к базе данных начинается с текущей директории D:\PythonProjectUni\Module_17_Resources>
# / — это разделитель пути в файловой системе
# taskmanager.db - файл бд SQLite

# Если autoflush=True, то перед каждым запросом (например, SELECT, UPDATE, DELETE) SQLAlchemy автоматически отправляет
# все ожидающие изменения (например, добавленные, измененные или удаленные объекты) в базу данных. Если autoflush=False,
# то изменения не отправляются автоматически, и их нужно явно сохранить с помощью session.commit() или session.flush()

r"""
Пошаговая инструкция по созданию базы данных и таблиц
Структура:
mtasks/
├── models/                       # Только SQLAlchemy-модели БД
│   ├── __init__.py               # Экспортирует SQLAlchemy-модели
│   ├── users.py                  # class User (SQLAlchemy)
│   └── tasks.py                  # class Task (SQLAlchemy)
│
├── schemas/                      # Pydantic-модели (если используются)
│                                 # UserCreate, UserResponse и т.д.
│                                 # TaskCreate, TaskResponse и т.д.
│
├── routers/                      # FastAPI-роутеры
│   ├── users.py                  # Использует Pydantic-модели из schemas/
│   └── tasks.py                  # и SQLAlchemy-модели из models/
│
└── backend/
    ├── db.py                     # engine, Base, SessionLocal
    └── create_db.py              # Создает таблицы SQL
    
1. Настройка подключения к БД (db.py)
# mtasks/backend/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

# 1.1. Создаем папку для БД (если не существует)
db_dir = Path(__file__).parent  # Папка backend
os.makedirs(db_dir, exist_ok=True)
# 1.2. Настраиваем путь к SQLite (относительно корня проекта)
DATABASE_URL = "sqlite:///mtasks/backend/taskmanager.db"
# 1.3. Создаем движок с логированием SQL
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Вывод SQL-запросов в консоль)
# 1.4. Настраиваем сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 1.5. Базовый класс для моделей
Base = declarative_base()
2. Создание моделей (models/)
... и их импорт в __init__
# mtasks/models/__init__.py
from .users import User
from .tasks import Task
3. Создание скрипта инициализации (create_db.py)
# mtasks/backend/create_db.py
from mtasks.backend.db import engine, Base
from mtasks.models import User, Task  # Важно: импорт моделей!
if __name__ == "__main__":
    # Создаем все таблицы и выводим SQL
    Base.metadata.create_all(engine)
4. Запуск инициализации
# Переходим в корень проекта
cd D:\PythonProjectUni\Module_17_Resources
# Запускаем создание таблиц
python -m mtasks.backend.create_db
5. Ожидаемый результат
    В консоли выводятся SQL-запросы:
CREATE TABLE users (...)
CREATE TABLE tasks (...)
    Файл БД создается по пути:
D:\PythonProjectUni\Module_17_Resources\mtasks\backend\taskmanager.db
    Проверка через dir mtasks\backend показывает:
taskmanager.db    # Файл базы данных
__pycache__       # Кэш Python
db.py             # Настройки БД
create_db.py      # Скрипт инициализации

 Итоговая последовательность
Настроить db.py (путь + движок)
Создать модели в models/
Импортировать модели в models/__init__.py
Создать create_db.py с вызовом create_all()
Запустить скрипт из корня проекта
Теперь ваша БД готова к использованию! Для работы с данными используйте SessionLocal из db.py.

Ошибки при открытии taskmanager.db
Файл БД SQLite — бинарный, его нельзя редактировать как текст. Рекомендации:
    "Plugins supporting *.db found":
Лучший вариант: Install Simple SqliteBrowser plugin (плагин PyCharm для просмотра БД)
Альтернатива: Используйте сторонние программы:
    DB Browser for SQLite (бесплатно)
    SQLite CLI (sqlite3 taskmanager.db в терминале)

"The file was explicitly reassigned to a plain text":
    Выберите Remove association (файл БД не является текстовым)
Или настройте PyCharm:
    Settings | Editor | File Types → удалите .db из текстовых типов
"Wrong encoding UTF-8":
    Нажмите Ignore (SQLite-файлы не используют текстовую кодировку)
    Если продолжите открывать как текст — увидите "бинарный мусор"


ОТКРЫТИЕ И ПРОСТОТР БАЗЫ ДАННЫХ
Шаг 1: Открытие базы данных
Запустите программу → нажмите «Open Database»
    Перейдите в папку вашего проекта:
    D:\PythonProjectUni\Module_17_Resources\mtasks\backend\
    Выберите файл taskmanager.db → «Открыть»
Шаг 3: Просмотр таблиц
Во вкладке «Database Structure» вы увидите список таблиц (users, tasks).
Чтобы посмотреть данные:
    Выберите таблицу → вкладка «Browse Data»
    Для SQL-запросов: вкладка «Execute SQL» (например, SELECT * FROM users;)
Шаг 4: Редактирование данных
Добавление строки:
Вкладка «Browse Data» → кнопка «New Record» (или Insert в SQL).
    Изменение данных:
    Двойной клик по ячейке → ввод значения → «Apply».
Удаление:
    Выделите строку → кнопка «Delete Record».
Шаг 5: Экспорт/Импорт
Экспорт в CSV/JSON:
    «File» → «Export» → «Table(s) to CSV/JSON...».
Импорт данных:
    «File» → «Import» → «Table from CSV/JSON...».

Шаг 6: Визуализация связей
Во вкладке «Database Structure»:
Нажмите на таблицу tasks → увидите связь user_id → users.user_id.
Для сложных запросов используйте «Execute SQL»:
sql
Copy
SELECT tasks.title, users.username 
FROM tasks 
JOIN users ON tasks.user_id = users.user_id;

"""