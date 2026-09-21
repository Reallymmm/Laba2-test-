// app.js — интерфейс списка задач (Лекция 2).
// Отвечает за отрисовку (работа с DOM) и обработку событий пользователя.
// За хранение данных отвечает объект store (см. store.js).

const listEl = document.getElementById("list");
const formEl = document.getElementById("add-form");
const inputEl = document.getElementById("title");

// Перерисовать весь список из данных store
async function render() {
  const tasks = await store.getTasks();
  listEl.innerHTML = "";

  if (tasks.length === 0) {
    listEl.innerHTML = '<li class="empty">Пока нет задач</li>';
    return;
  }

  for (const t of tasks) {
    const li = document.createElement("li");
    li.className = "task" + (t.done ? " done" : "");

    // чекбокс «выполнено»
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = !!t.done;
    checkbox.addEventListener("change", async () => {
      await store.toggleTask(t.id, checkbox.checked);
      render();
    });

    // текст задачи
    const span = document.createElement("span");
    span.className = "title";
    span.textContent = t.title;

    // кнопка удаления
    const del = document.createElement("button");
    del.className = "del";
    del.textContent = "✕";
    del.addEventListener("click", async () => {
      await store.deleteTask(t.id);
      render();
    });

    li.append(checkbox, span, del);
    listEl.append(li);
  }
}

// Отправка формы — добавление новой задачи
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();                 // не перезагружать страницу
  const title = inputEl.value.trim();
  if (!title) return;
  await store.addTask(title);
  inputEl.value = "";
  render();
});

// Первичная отрисовка при загрузке страницы
render();
