from .db import engine, Base
# Относительные импорты работают внутри пакета
# Если create_db.py и db.py лежат в одной папке (backend/), то '.' в импорте ссылается на текущий пакет

from mtasks.models import User_sql, Task_sql    # Импорт SQLAlchemy-моделей перенес в db.py и вернул обратно,
# так как образуется циклическая зависимость: В create_db.py вы импортируете Base из db.py, db.py вы импортируете модели
# (from mtasks.models import User, Task), которые, также импортируют Base из db.py

# Включите логирование SQL (если ещё не включено в `db.py`) - комментирую так как там включено
# engine.echo = True

# Проверка, что модели зарегистрированы
# print(f"Модели в Base: {Base.metadata.tables.keys()}")  # Должно показать 'users' и 'tasks' - перенес в
# if __name__ == "__main__":

# Создать таблицы и вывести SQL
if __name__ == "__main__":
    # Base.metadata.drop_all(engine)
    print(f"Модели в Base: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(engine)

# генерирует и выполняет SQL-запросы CREATE TABLE для всех моделей, которые унаследованы от Base:
#   from mtasks.backend.db import engine, Base => Base = declarative_base() =>
#   class Task(Base):
#     __tablename__ = 'tasks'
#       ...                     => engine = create_engine(
#                                   DATABASE_URL,
#                                   connect_args={"check_same_thread": False},
#                                   echo=True
#                                   )

# Почему Base.metadata.create_all(engine) работает без импорта моделей?
# Base — это единая декларативная база (Declarative Base). Когда определяете модели (User и Task), они
# наследуются от Base и SQLAlchemy автоматом регистрирует их в Base.metadata
#
# Python загружает все зависимости при запуске
# Даже если в create_db.py нет прямого импорта моделей, они могут быть загружены через другие импорты в проекте, пример:
#   Если mtasks.backend.db (откуда импортируется Base) сам импортирует модели,
#   Или если модели зарегистрированы в __init__.py пакета models.
# SQLAlchemy хранит метаданные в Base.metadata
# Как только Python загружает класс модели (даже косвенно), она добавляется в Base.metadata.tables.
# Поэтому create_all() видит все таблицы.

# Где правильно импортировать SQLAlchemy-модели (User, Task)?
# Варианты:
# Место импорта	        Плюсы	                        Минусы
# db.py	                ✅ Все модели загружаются автоматически при создании Base
#                       ✅ Чистый create_db.py (не нужно дублировать импорты)	❌ Зависит от структуры проекта (если models/ — отдельный пакет, нужен абсолютный импорт)
# create_db.py	        ✅ Явный контроль (видно, какие модели используются)
#                       ✅ Работает, даже если db.py не импортирует модели	    ❌ Приходится дублировать импорты в других скриптах (например, в тестах или миграциях)
# Рекомендация:
# 👉 Импортируйте модели в db.py, если они всегда нужны при работе с БД.
# 👉 Импортируйте в create_db.py, если db.py используется в разных контекстах и не должен зависеть от моделей.

# Запуск create_db.py: через консоль или напрямую?
# Способ 1: Через модуль (python -m) — лучше!
#   cd D:\PythonProjectUni\Module_17_Resources
#   python -m mtasks.backend.create_db
#   ✅ Плюсы:
# Python корректно обрабатывает импорты (работают и абсолютные, и относительные).
# Не зависит от рабочей директории.
#
# Способ 2: Прямой запуск (python create_db.py) — рискованно
# cd D:\PythonProjectUni\Module_17_Resources\mtasks\backend
# python create_db.py
#   ❌ Минусы:
# Могут сломаться относительные импорты (from .db import engine).
# Рабочая директория влияет на путь к SQLite.

# Можно запускать create_db.py напрямую (без консольной команды python -m), но нужно учесть несколько важных моментов,
# чтобы избежать ошибок импорта и путей.
#   Как сделать, чтобы create_db.py работал при прямом запуске?
# Добавьте явные абсолютные импорты и проверку путей. Вот рабочий пример:
r"""
# Файл mtasks/backend/create_db.py
import os
import sys
from pathlib import Path

# Фикс для импортов: добавляем корень проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent.parent  # D:\PythonProjectUni\Module_17_Resources
sys.path.append(str(root_dir))

# Теперь можно использовать абсолютные импорты
from mtasks.backend.db import engine, Base
from mtasks.models.users import User  # Явный импорт моделей
from mtasks.models.tasks import Task

if __name__ == "__main__":
    print("Создание таблиц...")
    Base.metadata.create_all(engine)
    print("Готово! Таблицы созданы.")
"""
# Почему это работает?
# sys.path.append(root_dir)
# Добавляет корень проекта (Module_17_Resources) в PYTHONPATH, чтобы Python мог находить модули типа mtasks.
#
# Теперь абсолютные импорты (from mtasks.models import User) работают даже при прямом запуске.
# Явный импорт моделей (User, Task)
# SQLAlchemy регистрирует их в Base.metadata при загрузке модуля.
#
# Запуск через if __name__ == "__main__"
# Код выполняется только при прямом запуске файла (а не при импорте).
#
#   Как теперь запускать?
# Через двойной клик (если у вас ассоциация .py с Python):
# Просто откройте create_db.py в проводнике и запустите.
#
# Через IDE (PyCharm, VSCode и т.д.):
# Нажмите ▶️ (Run) в редакторе.
#
# Через консоль (альтернатива):
# python mtasks/backend/create_db.py
#
# Ограничения и подводные камни
# Рабочая директория должна быть правильной
# Если БД использует относительный путь (например, sqlite:///taskmanager.db), файл будет создаваться в той директории,
# откуда запущен скрипт.
#
# Лучше указывать явный путь (как в примере выше).
# Не забудьте добавить все модели в импорты. Если не импортировать User и Task, create_all() их не увидит.

# Итог
# Да, можно запускать create_db.py напрямую, но нужно:
# Добавить корень проекта в sys.path (чтобы работали абсолютные импорты).
# Явно импортировать все модели (User, Task и др.).
# Указать абсолютный путь к БД (если SQLite).
# Это избавит от необходимости вводить python -m в консоли.

# 1. Что делает Path(__file__)?
# __file__ — это встроенная переменная Python, которая содержит абсолютный путь к текущему файлу.
# Например, для create_db.py это может быть:
#
# Copy
# D:\PythonProjectUni\Module_17_Resources\mtasks\backend\create_db.py
# Path(__file__) преобразует этот путь в объект Path из модуля pathlib, с которым удобно работать.
#
# 2. Зачем нужны .parent?
# Каждый вызов .parent поднимается на одну директорию вверх в файловой системе.
# Пример для вашего проекта:
# Предположим, структура проекта такая:
# D:\PythonProjectUni\Module_17_Resources\    # Корень проекта (куда нужно добавить путь)
# ├── mtasks/
# │   ├── backend/
# │   │   ├── db.py
# │   │   └── create_db.py    # <-- Здесь вызывается Path(__file__)
# Тогда:
#
# Path(__file__) → D:\...\Module_17_Resources\mtasks\backend\create_db.py
# .parent → D:\...\Module_17_Resources\mtasks\backend\ (папка backend)
# .parent.parent → D:\...\Module_17_Resources\mtasks\ (папка mtasks)
# .parent.parent.parent → D:\...\Module_17_Resources\ (корень проекта)
#
# Почему именно 3 .parent?
# Потому что create_db.py находится на третьем уровне вложенности от корня:
#
# Module_17_Resources (корень)
# ↗ mtasks (1-й .parent)
# ↗ backend (2-й .parent)
# ↗ create_db.py (3-й .parent — исходный файл)
#
# Чтобы добраться до корня, нужно подняться на три уровня вверх.

# Как проверить, что путь правильный?
# Добавьте отладочный вывод в create_db.py:
# python
# Copy
# from pathlib import Path
#
# print("Текущий файл:", Path(__file__))
# print("1-й parent:", Path(__file__).parent)
# print("2-й parent:", Path(__file__).parent.parent)
# print("3-й parent:", Path(__file__).parent.parent.parent)
#
# # Вывод для вашей структуры:
# # Текущий файл: D:\PythonProjectUni\Module_17_Resources\mtasks\backend\create_db.py
# # 1-й parent: D:\...\mtasks\backend
# # 2-й parent: D:\...\mtasks
# # 3-й parent: D:\...\Module_17_Resources  # Это и есть корень!

