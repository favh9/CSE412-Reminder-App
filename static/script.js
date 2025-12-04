document.getElementById('reminder-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const res = await fetch('/api/reminders', {
    method: 'POST',
    body: formData
  });

  if (res.ok) {
    location.reload();
  }
});

async function deleteReminder(id) {
  const res = await fetch(`/api/reminders/${id}`, {
    method: 'DELETE'
  });
  if (res.ok) {
    location.reload();
  }
}

async function renameReminder(id, currentTitle) {
  const newTitle = prompt('Enter new title', currentTitle || '');
  if (newTitle === null) return; // user cancelled
  const trimmed = newTitle.trim();
  if (!trimmed) return;

  const res = await fetch(`/api/reminders/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: trimmed })
  });

  if (res.ok) {
    location.reload();
  } else {
    alert('Failed to rename reminder');
  }
}
