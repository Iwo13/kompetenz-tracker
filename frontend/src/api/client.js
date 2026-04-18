const BASE = 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  // Competencies
  getCompetencies: (name) => request(`/competencies/${name}`),

  // Users
  getUsers:   ()         => request('/users'),
  createUser: (body)     => request('/users', { method: 'POST', body: JSON.stringify(body) }),
  updateUser: (id, body) => request(`/users/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteUser: (id)       => request(`/users/${id}`, { method: 'DELETE' }),

  // Goals
  getGoals:   (userId)        => request(`/users/${userId}/goals`),
  saveGoal:   (userId, body)  => request(`/users/${userId}/goals`, { method: 'POST', body: JSON.stringify(body) }),
};
