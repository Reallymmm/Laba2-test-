"""Модуль работы с базой данных PostgreSQL (Лекция 3).

Вынесен отдельно от main.py для наглядности: вся работа с хранилищем собрана в
одном месте, а обработчики HTTP-запросов её только вызывают.

Используется драйвер ``psycopg`` (PostgreSQL) и «сырой» SQL. Параметры подключения
берутся из файла ``.env`` (в корне проекта) через переменные окружения — так удобно
переключать локальный запуск и запуск в Docker, не меняя код.

Переменные (см. ``.env`` / ``.env.example``):
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
Либо можно задать готовую строку целиком через ``DATABASE_URL`` (имеет приоритет),
формат: ``postgresql://<пользователь>:<пароль>@<хост>:<порт>/<база>``.

Примечание: в лекции ORM показывался на примере SQLAlchemy — это альтернатива
«сырому» SQL; здесь для минимальности оставлен чистый SQL.
"""

import os
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

# Загружаем .env из корня проекта (для локального запуска). В Docker переменные
# приходят из окружения контейнера, а .env в образ не копируется — тогда
# load_dotenv просто ничего не делает (файла нет).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _build_database_url() -> str:
    """Собрать строку подключения к PostgreSQL из переменных окружения.

    Приоритет у готовой ``DATABASE_URL``; иначе строка собирается из отдельных
    ``POSTGRES_*`` (у каждой есть дефолт для локального запуска).
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "todo")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = _build_database_url()


def _connect() -> psycopg.Connection:
    """Открыть соединение с PostgreSQL по DATABASE_URL."""
    return psycopg.connect(DATABASE_URL)


def init_db(retries: int = 10, delay: float = 1.0) -> None:
    """Создать таблицу задач, если её нет.

    При старте в Docker база может подниматься дольше приложения, поэтому
    подключение повторяется несколько раз с паузой (ожидание готовности БД).
    """
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with _connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id    SERIAL  PRIMARY KEY,
                        title TEXT    NOT NULL,
                        done  BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
            return
        except psycopg.OperationalError as exc:  # БД ещё не готова принимать соединения
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Не удалось подключиться к БД: {last_error}")


def get_tasks() -> list[dict]:
    """Вернуть все задачи, отсортированные по id."""
    with _connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            return cur.fetchall()


def add_task(title: str) -> dict:
    """Добавить задачу и вернуть созданную запись (id генерирует БД)."""
    with _connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
                (title,),
            )
            return cur.fetchone()


def set_done(task_id: int, done: bool) -> None:
    """Изменить статус «выполнено» для задачи."""
    with _connect() as conn:
        conn.execute("UPDATE tasks SET done = %s WHERE id = %s", (done, task_id))


def delete_task(task_id: int) -> None:
    """Удалить задачу по id."""
    with _connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
