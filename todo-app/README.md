# Учебный проект «Список задач»

Один и тот же проект постепенно **обрастает функционалом от лекции к лекции**.
Каждая лекция добавляет свои файлы/модули — ничего из предыдущих не переписывается «с нуля».

## Что добавляет каждая лекция

### Лекция 1 «Введение в web» — статическая страница
Файлы:
- `frontend/index.html` — структура страницы (HTML);
- `frontend/styles.css` — оформление (блок с пометкой «Лекция 1»).

**Запуск:** открыть `frontend/index.html` двойным кликом в браузере.
Видны заголовок и оформление; список пока пустой (JS ещё нет).

### Лекция 2 «Frontend» — интерактив в браузере
Файлы:
- `frontend/app.js` — работа с DOM и обработка событий (добавить / отметить / удалить);
- `frontend/store.js` — слой хранения; на этом этапе данные лежат в `localStorage`;
- в `styles.css` добавлены раскладка формы (Flexbox) и адаптивность (медиазапрос).

**Запуск:** открыть `frontend/index.html` в браузере. Задачи добавляются и
сохраняются прямо в браузере — сервер не нужен.

### Лекция 3 «Backend» — сервер, REST API и PostgreSQL
Файлы:
- `backend/main.py` — FastAPI: REST API `/api/tasks` и отдача фронтенда;
- `backend/database.py` — отдельный модуль работы с БД (**PostgreSQL**, драйвер `psycopg`);
- `backend/requirements.txt` — зависимости;
- `frontend/store.js` теперь сначала обращается к `/api/tasks`, а `localStorage`
  остаётся резервом (если сервер недоступен).

Конфигурация БД — в файле **`.env`** (переменные `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`). Перед запуском скопируйте шаблон:
```bash
cp .env.example .env      # Windows: copy .env.example .env
```
Значения по умолчанию уже рабочие. `backend/database.py` читает `.env` через
`python-dotenv`.

**Запуск (проще всего — через Docker из Лекции 4, он поднимет и БД):**
```bash
docker compose up --build
# открыть http://localhost:8000
```

**Запуск без Docker (нужен установленный PostgreSQL):**
```bash
createdb -U postgres todo         # создать базу (один раз)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# открыть http://localhost:8000
```
Параметры берутся из `.env` (хост по умолчанию `localhost`). Теперь задачи хранятся
в PostgreSQL и не пропадают при закрытии браузера.

### Лекция 4 «Docker» — запуск в контейнерах
Файлы:
- `Dockerfile` — образ с backend и фронтендом;
- `docker-compose.yml` — два сервиса: `web` (приложение) и `db` (PostgreSQL);
  данные БД хранятся в томе `pgdata`.

**Запуск:**
```bash
docker compose up --build     # поднять приложение + БД
# открыть http://localhost:8000
docker compose down           # остановить (данные БД сохранятся)
docker compose down -v        # остановить и удалить данные БД
```

## Структура проекта
```
todo-app/
├── README.md
├── .env.example         # Л3: шаблон конфигурации (скопировать в .env)
├── .env                 # Л3: локальная конфигурация (в .gitignore)
├── frontend/            # Лекции 1–2
│   ├── index.html       # Л1: структура
│   ├── styles.css       # Л1: стили; Л2: Flexbox + адаптив
│   ├── app.js           # Л2: DOM и события
│   └── store.js         # Л2: localStorage; Л3: + REST API
├── backend/             # Лекция 3
│   ├── main.py          # FastAPI: /api/tasks + отдача фронтенда
│   ├── database.py      # PostgreSQL через psycopg; конфиг из .env (python-dotenv)
│   └── requirements.txt
├── Dockerfile           # Лекция 4
├── docker-compose.yml   # Лекция 4: web + db (PostgreSQL), env_file: .env
├── .dockerignore
└── .gitignore
```

## Идея прогрессии
Интерфейс (`app.js`) обращается к абстракции `store` и **не знает**, откуда берутся
данные. Меняется только реализация хранения: `localStorage` в браузере (Лекция 2) →
REST API + база данных **PostgreSQL** на сервере (Лекция 3). Это наглядно показывает
разделение слоёв: frontend, backend, база данных — и то, как каждый следующий уровень
достраивается поверх предыдущего.
