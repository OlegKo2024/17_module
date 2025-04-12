r"""
Alembic: Управление миграциями базы данных в FastAPI + SQLAlchemy

Что такое Alembic?
Alembic - это инструмент для миграций баз данных, созданный специально для работы с SQLAlchemy. Он позволяет:
Создавать и применять изменения структуры БД (схемы)
Откатывать изменения при необходимости
Поддерживать историю изменений структуры БД
Автоматически генерировать миграции на основе изменений в моделях SQLAlchemy

Зачем нужен Alembic?
Без Alembic:
При изменении моделей SQLAlchemy вам нужно вручную изменять структуру БД
Нет истории изменений
Сложно работать в команде (каждый должен вручную применять изменения)
Нет простого способа отката изменений

С Alembic:
Автоматическая генерация миграций
Контроль версий структуры БД
Простое применение/откат изменений
Совместимость с CI/CD

1. Установка Alembic
pip install alembic

2. Настройка Alembic в вашем проекте
Инициализация Alembic (в корне проекта):
alembic init alembic
Эта команда создаст:

your_project/
├── alembic/
│   ├── env.py             # Основной конфигурационный файл
│   ├── script.py.mako     # Шаблон для новых миграций
│   └── versions/          # Папка с миграциями
├── alembic.ini            # Конфигурационный файл
└── ...                    # Остальная структура проекта

3. Настройка alembic.ini:
Замените строку подключения на свою строку подключения к БД, например:
есть: sqlalchemy.url = driver://user:pass@localhost/dbname
стало: sqlalchemy.url = sqlite:///backend/taskmanager.db - без кавычек и относительно текущей директории .mtasks!

Проверка корректности подключения:
Запустить alembic current из папки, где лежит alembic.ini — из D:\PythonProjectUni\Module_17_Resources\mtasks
Все команды Alembic запускайте из папки, где лежит alembic.ini - mtasks в данном случае
Проверка структуры проекта:
D:\PythonProjectUni\Module_17_Resources\
└── mtasks\
    ├── alembic.ini               # Конфиг Alembic
    ├── alembic\                  # Папка с миграциями
    ├── backend\
    │   └── taskmanager.db        # Файл БД
    └── ...                       # Остальные файлы проекта

4. Настройка alembic/env.py: Замените содержимое на:
from logging.config import fileConfig - без изменений
from sqlalchemy import create_engine - лучше использовать create_engine (более явный контроль). Почему?
    create_engine даёт прямой контроль над подключением к БД.
    engine_from_config используется для сложных конфигов (например, из alembic.ini), но менее гибок
    Однако, возникает ошибка рекомендовано оставить как по умолчанию: from logging.config import fileConfig

from mtasks.backend.db import Base
    Почему абсолютный путь?
    Файл alembic/env.py находится вне пакета mtasks (в папке alembic/ на том же уровне, что и mtasks/)
    Python не видит mtasks как часть текущего пакета, поэтому нужен полный путь
from models.users import User, Task
    Почему относительный путь?
        Alembic автоматически добавляет корень проекта (D:\PythonProjectUni\Module_17_Resources\) в sys.path
        Папка mtasks становится доступна для импорта напрямую
        Эквивалентно from mtasks.models import ..., но короче
    Как Python ищет модули?
        Когда вы запускаете Alembic из корня проекта (mtasks/), Python добавляет в путь поиска:
        Директорию запуска D:\PythonProjectUni\Module_17_Resources\mtasks\
        Пути из переменной PYTHONPATH - поэтому оба варианта работают:
            from models import User_sql          # Короткая форма (рекомендуется)
            from mtasks.models import User_sql   # Абсолютная форма

from alembic import context

# Это нужно для автоматического обнаружения моделей
target_metadata = Base.metadata

# Импорт ваших моделей SQLAlchemy
# Это необходимо для их обнаружения Alembic
def run_migrations_offline():
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(context.config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
Работа с миграциями

Создание первой миграции (если БД уже существует):
alembic revision --autogenerate -m "Initial migration"
Применение миграций:
alembic upgrade head
Откат миграции:
alembic downgrade -1
Интеграция с вашей структурой проекта
В backend/db.py убедитесь, что у вас есть:

python
Copy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/mtasks"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
В create_db.py можно оставить:

python
Copy
from .db import Base, engine

def init_db():
    Base.metadata.create_all(bind=engine)
Но после настройки Alembic этот файл можно использовать только для первоначального создания БД.

Рабочий процесс с Alembic
Вносите изменения в модели SQLAlchemy

Создаете миграцию:

bash
Copy
alembic revision --autogenerate -m "Описание изменений"
Проверяете сгенерированный файл миграции в alembic/versions/

Применяете миграцию:

bash
Copy
alembic upgrade head
Важные замечания
Всегда проверяйте автоматически сгенерированные миграции перед применением

Не изменяйте уже примененные миграции

Храните файлы миграций в системе контроля версий

Для production используйте отдельные настройки подключения к БД

Советы по организации
Для разных окружений (dev/test/prod) используйте разные .env файлы

Можно добавить хуки в alembic/env.py для дополнительной валидации

Рассмотрите возможность использования alembic.op для сложных миграций

Ключевые отличия от ручного подхода
Действие	Без Alembic	С Alembic
Добавление поля	Ручной SQL или пересоздание БД	Автогенерация миграции
Откат изменений	Нет стандартного механизма	alembic downgrade
Работа в команде	Каждый делает изменения вручную	Все применяют одинаковые миграции
История изменений	Нет	Полная версионность
Перенос данных	Сложно и рискованно	Возможность писать миграции Python
Вывод: Alembic даёт вам контроль над эволюцией схемы БД так же, как git даёт контроль над изменениями кода.
Это особенно критично, когда ваше приложение уже в production и содержит важные данные.
"""