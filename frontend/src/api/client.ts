import type { User, Area, Rotation, Ausbildungsplatz, GoalEntry } from '../types';

const BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

interface CompetenciesResponse { areas: Area[] }
interface UsersResponse        extends Array<Omit<User, 'goals' | 'rotations' | 'startDate'>> {}
interface AusbildungsplaetzeResponse { ausbildungsplaetze: Ausbildungsplatz[] }

export const api = {
  // Competencies
  getCompetencies: (name: string) =>
    request<CompetenciesResponse>(`/competencies/${name}`),

  // Users
  getUsers:   () =>
    request<UsersResponse>('/users'),
  createUser: (body: Partial<User>) =>
    request<User>('/users', { method: 'POST', body: JSON.stringify(body) }),
  updateUser: (id: string, body: Partial<User>) =>
    request<User>(`/users/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteUser: (id: string) =>
    request<void>(`/users/${id}`, { method: 'DELETE' }),

  // Goals
  getGoals: (userId: string) =>
    request<Array<{ goal_id: string; level: string; comment: string; updated_at: string }>>(
      `/users/${userId}/goals`
    ),
  saveGoal: (userId: string, goalId: string, body: Partial<GoalEntry> & { goal_id: string }) =>
    request<GoalEntry>(`/users/${userId}/goals/${goalId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  // Rotationen
  getRotations:   (userId: string) =>
    request<Rotation[]>(`/users/${userId}/rotations`),
  addRotation:    (userId: string, body: Partial<Rotation>) =>
    request<Rotation>(`/users/${userId}/rotations`, { method: 'POST', body: JSON.stringify(body) }),
  updateRotation: (userId: string, rotId: string, body: Partial<Rotation>) =>
    request<Rotation>(`/users/${userId}/rotations/${rotId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  deleteRotation: (userId: string, rotId: string) =>
    request<void>(`/users/${userId}/rotations/${rotId}`, { method: 'DELETE' }),

  // Ausbildungsplätze
  getAusbildungsplaetze: () =>
    request<AusbildungsplaetzeResponse>('/ausbildungsplaetze'),
  updateApBereiche: (code: string, bereiche: string[]) =>
    request<Ausbildungsplatz>(`/ausbildungsplaetze/${code}/bereiche`, {
      method: 'PUT',
      body: JSON.stringify({ bereiche }),
    }),
  updateApHk: (code: string, bildungsplan: string, hk_id: string, coverage: string) =>
    request<Ausbildungsplatz>(`/ausbildungsplaetze/${code}/hk`, {
      method: 'PUT',
      body: JSON.stringify({ bildungsplan, hk_id, coverage }),
    }),
  createAusbildungsplatz: (body: Partial<Ausbildungsplatz>) =>
    request<Ausbildungsplatz>('/ausbildungsplaetze', { method: 'POST', body: JSON.stringify(body) }),
};
