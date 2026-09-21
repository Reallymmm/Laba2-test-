# Лекция 4: контейнеризация учебного приложения.
# Один образ: backend (FastAPI) + отдача статического фронтенда.

FROM python:3.13-slim

WORKDIR /app

# 1) Сначала зависимости — этот слой кешируется и не пересобирается,
#    пока requirements.txt не изменился.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 2) Затем код приложения: backend + статический фронтенд.
COPY backend ./backend
COPY frontend ./frontend

WORKDIR /app/backend
EXPOSE 8000

# Запуск сервера. 0.0.0.0 — слушать снаружи контейнера.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
