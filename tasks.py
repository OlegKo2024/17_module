"""
В модуле task.py напишите APIRouter с префиксом '/task' и тегом 'task', а также следующие маршруты, с пустыми функциями:
    get '/' с функцией all_tasks.
    get '/task_id' с функцией task_by_id.
    post '/create' с функцией create_task.
    put '/update' с функцией update_task.
    delete '/delete' с функцией delete_task.

В случае ниже не обязательно делать все функции async в FastAPI. Использование async зависит от того, выполняет ли
функция асинхронные операции (например, запросы к базе данных, вызовы внешних API и т. д.). Здесь этого нет.
"""

from fastapi import APIRouter, HTTPException
from mtasks.schemas import Task, CreateTask, UpdateTask

from mtasks.models import Task_sql

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)

# список объектов
# Типизация users: list[Task] = []:
# Запись users: list[Task] = [] значит, что переменная users есть список и должен содержать только объекты типа Task
# Это аннотация типа, которая помогает: Улучшить читаемость кода. Проверить типы данных на этапе разработки (например,
# с помощью инструментов вроде mypy). Получить подсказки в IDE (например, PyCharm. Однако, Python не проверяет типы
# данных во время выполнения, поэтому эта аннотация не накладывает ограничений на содержимое списка
tasks: list[Task] = []  # Список tasks хранит объекты типа Task.


@router.get("/", response_model=list[Task])
async def get():
    return tasks


@router.get("/{slug}", response_model=Task)
async def task_by_id(slug: str):
    for t in tasks:
        if t.slug == slug:
            return t
    raise HTTPException(status_code=404, detail="Задача не найдена")


@router.post("/create", response_model=Task)    # FastAPI ждет, что функция вернёт объект типа response_model=Task
async def create_task(task: CreateTask):
    if any(task.title == t.title for t in tasks):
        raise HTTPException(status_code=400, detail="Task already exists")
    if any(task.slug == t.slug for t in tasks):
        raise HTTPException(status_code=400, detail="Slug already exists")
    new_id = max((t.task_id for t in tasks), default=0) + 1
    new_task = Task(
        task_id=new_id,
        title=task.title,
        content=task.content,
        priority=task.priority,
        completed=task.completed,
        slug=task.slug,
        user_id=task.user_id
    )
    tasks.append(new_task)
    return new_task


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task: UpdateTask):
    for t in tasks:
        if t.task_id == task_id:
            t.title = task.title
            t.content = task.content
            t.priority = task.priority
            t.completed = task.completed
            t.slug = task.slug
            t.user_id = task.user_id
            return t
    raise HTTPException(status_code=404, detail="Задача не найдена")


@router.patch("/{task_id}", response_model=Task)
async def update_task_patch(task_id: int, task: UpdateTask):
    task_to_update = next((t for t in tasks if t.task_id == task_id), None) # Что делает:
    # Перебирает список tasks (где t — объекты задач).
    # Находит первый объект, у которого t.task_id == task_id.
    # Если не находит, возвращает None.
    if not task_to_update:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = task.model_dump(exclude_unset=True, exclude_none=True)    # Что делает:
    # task — это Pydantic-модель UpdateTask, переданная в запросе.
    # .model_dump() конвертирует её в словарь.
    # exclude_unset=True — исключает поля, которые не были переданы в запросе.
    # exclude_none=True — исключает поля со значением None.
    for field, value in updates.items():
        setattr(task_to_update, field, value)  # Обновляем поля модели
        # Что делает:
        # updates.items() возвращает пары (ключ, значение) из словаря.
        # setattr(obj, field, value) — это встроенная функция Python, которая:
        # Берёт объект task_to_update.
        # Находит его атрибут с именем field (например, title).
        # Присваивает ему value (например, "New title").
    return task_to_update


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t.task_id == task_id:
            del tasks[i]    # .remove(элемент) не подходит - надо указать элемент списка, не индекс
            # del_task = tasks.pop(i)
            return {'Message': f'Task {task_id} {t.title} удален'}
            # return {'Deleted Task': del_task}
    raise HTTPException(status_code=404, detail="Задача не найдена")

# @router.delete("/delete}")
# def delete_task(task_id: int):
#     """Удалить продукт"""
#     global tasks
#     tasks = [t for t in tasks if t.task_id != task_id]
#     return {"message": f"Task {task_id} deleted"}

# Если tasks — это список словарей, используйте t["task_id"].
# Если tasks — это список объектов, используйте t.task_id и преобразуйте объект в словарь

"""
    del t[i]: Удаляет элемент по индексу i из списка t и Не возвращает удалённый элемент
t = [1, 2, 3, 4]
del t[1]  # Удаляет элемент с индексом 1 (число 2)
print(t)  # [1, 3, 4]
    t.pop(i): Удаляет по индексу i и возвращает его. Если индекс не указан (t.pop()), удаляет и возвращает последний 
элемент списка. Пример:
t = [1, 2, 3, 4]
removed_element = t.pop(1)  # Удаляет элемент с индексом 1 (число 2)
print(t)  # [1, 3, 4]
print(removed_element)  # 2
    t.remove(x): Удаляет первый элемент в списке, значение которого равно x. Если элемент не найден, вызывает ValueError
t = [1, 2, 3, 4, 2]
t.remove(2)  # Удаляет первое вхождение числа 2
print(t)  # [1, 3, 4, 2]
"""

"""
Итоговые правила по global
Ситуация	           Нужен global?	Пример
Изменение mutable-объекта	❌ Нет	list.append(), dict.update
Переприсваивание mutable	✅ Да	list = [1, 2, 3]
Любая операция с immutable	✅ Да	str += "new", int += 1
Выводы
В вашем примере с del tasks[i] global не нужен, так как список изменяется, но не переприсваивается.

Для строк, чисел и других immutable-объектов global обязателен при любых "изменениях".

Это общее правило Python, а не особенность FastAPI.
"""