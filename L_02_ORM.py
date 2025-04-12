"""
Введение в SQLAlchemy и ORM
Что такое SQLAlchemy?
SQLAlchemy — это популярная библиотека Python для работы с базами данных. Она предлагает как низкоуровневые
SQL-интерфейсы, так и высокоуровневый ORM (Object-Relational Mapping).

Что такое ORM?
ORM (Object-Relational Mapping) — это способ связи объектов вашего приложения с таблицами базы данных.
ORM — это технология, которая связывает объекты в коде с записями в реляционной базе данных.
ORM позволяет работать с базой данных, используя объекты и методы, вместо написания SQL-запросов вручную.


    Класс Python = Таблица в базе данных.
    Объект класса = Строка в таблице.
    Поля класса = Колонки таблицы.

Этот подход позволяет:

    Упрощать взаимодействие с базой данных.
    Использовать объекты Python вместо SQL-запросов.
    Сосредотачиваться на логике приложения, а не на SQL-коде.

ORM (Object-Relational Mapping) — это технология, которая связывает объекты Python с таблицами базы данных, превращая
работу с БД в более интуитивный и "питонический" процесс. Вот как это работает на практике:
1. Превращение таблиц в классы Python (МОДЕЛИ)
ORM автоматически отображает таблицы БД на классы Python (МОДЕЛИ), а строки в таблицах — на экземпляры объектов.
Пример (с использованием SQLAlchemy):
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Таблица `users` превращается в класс:
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
Теперь каждая запись в таблице users — это объект класса User.

2. Замена SQL-запросов на методы объектов
Вместо написания SQL вручную вы работаете с объектами и их методами. ORM сам генерирует нужные запросы.
Примеры операций:
Добавление записи (аналог INSERT):
    new_user = User(name="Анна", email="anna@example.com")
    session.add(new_user)  # ORM создаст SQL-запрос автоматически
    session.commit()
Выборка данных (аналог SELECT):
users = session.query(User).filter_by(name="Анна").all()  # Превращается в SELECT * FROM users WHERE name='Анна'

3. Управление отношениями между таблицами
ORM упрощает работу со связями (один-ко-многим, многие-ко-многим) через атрибуты объектов.
Пример связи "один-ко-многим" (у пользователя много статей):
class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))  # Связь с таблицей users
    author = relationship("User", back_populates="articles")  # Доступ через объект

# Теперь можно так:
user = session.query(User).first()
for article in user.articles:  # ORM сам подгрузит связанные статьи
    print(article.title)

4. Транзакции и управление сессиями
ORM контролирует целостность данных через сессии (например, откатывает изменения при ошибке):
try:
    user = User(name="Петр")
    session.add(user)
    session.commit()  # Фиксация изменений
except:
    session.rollback()  # Откат при ошибке

Популярные ORM для Python:
SQLAlchemy (гибкость + поддержка низкоуровневого SQL).

Django ORM (простота, но привязан к Django).

Peewee (легковесный вариант для небольших проектов).

Итог: ORM — это "мост" между Python-объектами и реляционными данными, который экономит время, но требует
понимания его механизмов.

"""