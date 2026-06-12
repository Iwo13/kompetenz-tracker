import type { User, Area, Rotation, Ausbildungsplatz, GoalEntry, UserDocument, DocumentGoalLink } from '../types';

const BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

async function upload<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: 'POST', body: formData });
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
    request<Array<{
      goal_id: string;
      effective_level: number;
      manual_level: number;
      comment: string | null;
      updated_at: string | null;
      document_contributions: Array<{ doc_id: string; doc_title: string; bloom_level: number }>;
    }>>(
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

  // Dokumente
  getDocuments: (userId: string) =>
    request<UserDocument[]>(`/users/${userId}/documents`),
  uploadDocument: (userId: string, formData: FormData) =>
    upload<UserDocument>(`/users/${userId}/documents`, formData),
  updateDocument: (userId: string, docId: string, body: {
    title: string; description?: string; ap_code: string; goal_ids: string[];
    kurzbeschreibung?: string; umsetzung?: string; luecken?: string;
    feedback_berufsbildner?: string;
  }) =>
    request<UserDocument>(`/users/${userId}/documents/${docId}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteDocument: (userId: string, docId: string) =>
    request<void>(`/users/${userId}/documents/${docId}`, { method: 'DELETE' }),
  getDocumentFileUrl: (userId: string, docId: string) =>
    `${BASE}/users/${userId}/documents/${docId}/file`,
  updateDocumentGoal: (userId: string, docId: string, goalId: string, body: { einschaetzung?: string | null; bloom_level?: number | null }) =>
    request<DocumentGoalLink>(`/users/${userId}/documents/${docId}/goals/${goalId}`, { method: 'PUT', body: JSON.stringify(body) }),
  aiEvaluateDocument: (userId: string, docId: string) =>
    request<UserDocument>(`/users/${userId}/documents/${docId}/ai-evaluate`, { method: 'POST' }),
};
