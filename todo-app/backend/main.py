"""Backend учебного приложения на FastAPI (Лекция 3).

Что здесь есть:
- REST API для задач: /api/tasks (GET, POST, PATCH, DELETE);
- отдача статического фронтенда (frontend/) — чтобы весь проект открывался
  по одному адресу http://localhost:8000 без проблем с CORS.

Запуск:
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import database

app = FastAPI(title="Список задач — учебный пример")

# Создаём таблицу при старте приложения
database.init_db()


# --- Модели тела запроса (валидация входных данных) ---
class TaskIn(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    done: bool


# --- REST API ---
@app.get("/api/tasks")
def list_tasks() -> list[dict]:
    """Список всех задач."""
    return database.get_tasks()


@app.post("/api/tasks")
def create_task(task: TaskIn) -> dict:
    """Создать задачу."""
    return database.add_task(task.title)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, upd: TaskUpdate) -> dict:
    """Отметить задачу выполненной/невыполненной."""
    database.set_done(task_id, upd.done)
    return {"status": "updated", "id": task_id, "done": upd.done}


@app.delete("/api/tasks/{task_id}")
def remove_task(task_id: int) -> dict:
    """Удалить задачу."""
    database.delete_task(task_id)
    return {"status": "deleted", "id": task_id}


# --- Отдача фронтенда ---
# Монтируется ПОСЛЕ API-маршрутов, чтобы /api/* обрабатывались обработчиками выше,
# а всё остальное отдавалось как статические файлы (index.html, styles.css, ...).
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
