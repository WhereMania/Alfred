async function fetchTasks() {
  const response = await fetch("/tasks");
  const tasks = await response.json();
  const taskList = document.getElementById("taskList");
  taskList.innerHTML = ""; // Clear existing tasks

  tasks.forEach((task) => {
    const li = document.createElement("li");
    li.textContent = task[1] + " - " + task[2]; // task title and status
    li.id = `task-${task[0]}`; // Set the ID for deletion/updating

    const completeButton = document.createElement("button");
    completeButton.textContent = "Complete";
    completeButton.onclick = () => completeTask(task[0]);

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.onclick = () => deleteTask(task[0]);

    li.appendChild(completeButton);
    li.appendChild(deleteButton);
    taskList.appendChild(li);
  });
}

async function addTask() {
  const taskInput = document.getElementById("taskInput");
  const task = taskInput.value;

  if (task) {
    await fetch("/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ task }),
    });
    taskInput.value = ""; // Clear input
    fetchTasks(); // Refresh task list
  }
}

async function deleteTask(taskId) {
  await fetch(`/delete_task/${taskId}`, {
    method: "DELETE",
  });
  fetchTasks(); // Refresh task list
}

async function completeTask(taskId) {
  await fetch(`/complete_task/${taskId}`, {
    method: "PUT",
  });
  fetchTasks(); // Refresh task list
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("addTaskButton").addEventListener("click", addTask);
  fetchTasks(); // Load tasks on page load
});
