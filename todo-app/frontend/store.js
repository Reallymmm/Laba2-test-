// store.js — слой хранения данных списка задач.
//
// Лекция 2: данные хранились в localStorage браузера — сервер не нужен,
//           страница работает при открытии файла напрямую (file://).
// Лекция 3: появился backend. Тот же интерфейс теперь сначала ходит в REST API
//           (/api/tasks), а localStorage остаётся резервом, если сервера нет
//           (graceful fallback). Интерфейс store не меняется — app.js не важно,
//           откуда берутся данные.

const LS_KEY = "todo.tasks";

function lsGet() {
  return JSON.parse(localStorage.getItem(LS_KEY) || "[]");
}

function lsSet(tasks) {
  localStorage.setItem(LS_KEY, JSON.stringify(tasks));
}

const store = {
  // Получить список задач
  async getTasks() {
    try {
      const res = await fetch("/api/tasks");
      if (!res.ok) throw new Error("API недоступен");
      return await res.json();               // Лекция 3: данные с сервера
    } catch {
      return lsGet();                         // Лекция 2: данные из localStorage
    }
  },

  // Добавить задачу
  async addTask(title) {
    try {
      const res = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      const tasks = lsGet();
      const task = { id: Date.now(), title, done: 0 };
      tasks.push(task);
      lsSet(tasks);
      return task;
    }
  },

  // Переключить статус «выполнено»
  async toggleTask(id, done) {
    try {
      const res = await fetch(`/api/tasks/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ done }),
      });
      if (!res.ok) throw new Error();
    } catch {
      const tasks = lsGet().map((t) => (t.id === id ? { ...t, done: done ? 1 : 0 } : t));
      lsSet(tasks);
    }
  },

  // Удалить задачу
  async deleteTask(id) {
    try {
      const res = await fetch(`/api/tasks/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error();
    } catch {
      lsSet(lsGet().filter((t) => t.id !== id));
    }
  },
};
