import {
  createContext, useContext, useState, useEffect, useCallback,
  type ReactNode,
} from 'react';
import { api } from '../api/client';
import type {
  User, Area, Ausbildungsplatz, Rotation, Specialty, Role, BloomLevel, UserDocument, DocumentGoalLink,
  GoalContribution,
} from '../types';

// ── Typen ─────────────────────────────────────────────────────────────────────

interface AppContextValue {
  users:              User[];
  currentUser:        User | null;
  areas:              Area[];
  areasInformatiker:  Area[];
  areasIct:           Area[];
  loading:            boolean;
  error:              string | null;
  role:               Role;
  setRole:            (r: Role) => void;
  ausbildungsplaetze: Ausbildungsplatz[];
  currentAP:          Ausbildungsplatz | null;
  currentAPCode:      string | null;
  selectAP:           (code: string) => void;
  activeAP:           Ausbildungsplatz | null;
  rotationGanttView:    'lernende' | 'ausbildungsplaetze';
  setRotationGanttView: (v: 'lernende' | 'ausbildungsplaetze') => void;
  updateApHk:         (apCode: string, bildungsplan: string, hkId: string, coverage: string) => Promise<void>;
  addAusbildungsplatz:(body: Partial<Ausbildungsplatz>) => Promise<Ausbildungsplatz>;
  selectUser:         (id: string) => void;
  updateGoal:         (goalId: string, level: BloomLevel, comment: string) => Promise<void>;
  reloadGoals:        (userId: string) => Promise<void>;
  addUser:            (body: Partial<User>) => Promise<User>;
  editUser:           (id: string, body: Partial<User>) => Promise<void>;
  removeUser:         (id: string) => Promise<void>;
  addRotation:        (userId: string, body: Partial<Rotation>) => Promise<Rotation>;
  updateRotation:     (userId: string, rotId: string, body: Partial<Rotation>) => Promise<Rotation>;
  deleteRotation:     (userId: string, rotId: string) => Promise<void>;
  documents:          UserDocument[];
  uploadDocument:     (userId: string, formData: FormData) => Promise<UserDocument>;
  updateDocument:     (userId: string, docId: string, body: { title: string; description?: string; ap_code: string; goal_ids: string[]; kurzbeschreibung?: string; umsetzung?: string; luecken?: string; feedback_berufsbildner?: string; document_date?: string; }) => Promise<void>;
  deleteDocument:     (userId: string, docId: string) => Promise<void>;
  updateDocumentGoal:  (userId: string, docId: string, goalId: string, einschaetzung: string | null, bloomLevel: number | null) => Promise<DocumentGoalLink>;
  aiEvaluateDocument: (userId: string, docId: string) => Promise<{ document: UserDocument; prompt_tokens: number; completion_tokens: number; total_tokens: number }>;
}

const AppContext = createContext<AppContextValue | null>(null);

const COMPETENCY_FILE: Record<Specialty, string> = {
  platform:      'kompetenzen-informatiker-efz',
  app:           'kompetenzen-informatiker-efz',
  'ict-fachmann':'kompetenzen-ict-fachmann-efz',
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [users,              setUsers]              = useState<User[]>([]);
  const [currentUserId,      setCurrentUserId]      = useState<string | null>(null);
  const [areas,              setAreas]              = useState<Area[]>([]);
  const [loading,            setLoading]            = useState(true);
  const [error,              setError]              = useState<string | null>(null);
  const [role,               setRole]               = useState<Role>('berufsbildner');
  const [areasInformatiker,  setAreasInformatiker]  = useState<Area[]>([]);
  const [areasIct,           setAreasIct]           = useState<Area[]>([]);
  const [ausbildungsplaetze, setAusbildungsplaetze] = useState<Ausbildungsplatz[]>([]);
  const [currentAPCode,      setCurrentAPCode]      = useState<string | null>(null);
  const [rotationGanttView,  setRotationGanttView]  = useState<'lernende' | 'ausbildungsplaetze'>('lernende');
  const [documents,          setDocuments]          = useState<UserDocument[]>([]);

  useEffect(() => {
    async function init() {
      try {
        const [compInfo, compIct, userList, apData] = await Promise.all([
          api.getCompetencies('kompetenzen-informatiker-efz'),
          api.getCompetencies('kompetenzen-ict-fachmann-efz'),
          api.getUsers(),
          api.getAusbildungsplaetze(),
        ]);
        setAreasInformatiker(compInfo.areas);
        setAreasIct(compIct.areas);
        setAusbildungsplaetze(apData.ausbildungsplaetze);
        if (apData.ausbildungsplaetze.length > 0) {
          setCurrentAPCode(apData.ausbildungsplaetze[0].code);
        }

        const usersWithGoals = await Promise.all(
          userList.map(async (u) => {
            const [goalList, rotList] = await Promise.all([
              api.getGoals(u.id).catch(() => []),
              api.getRotations(u.id).catch(() => []),
            ]);
            const goals: User['goals'] = {};
            goalList.forEach(g => {
              goals[g.goal_id] = {
                level:         g.effective_level as BloomLevel,
                manual_level:  g.manual_level as BloomLevel,
                comment:       g.comment ?? '',
                date:          g.updated_at ?? undefined,
                contributions: (g.document_contributions ?? []).map((c): GoalContribution => ({
                  doc_id:      c.doc_id,
                  doc_title:   c.doc_title,
                  bloom_level: c.bloom_level,
                })),
              };
            });
            return { ...u, startDate: u.start_date, goals, rotations: rotList } as User;
          })
        );
        setUsers(usersWithGoals);
        if (usersWithGoals.length > 0) {
          setCurrentUserId(usersWithGoals[0].id);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unbekannter Fehler');
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const currentUser = users.find(u => u.id === currentUserId) ?? null;

  useEffect(() => {
    if (!currentUser) return;
    const allAreas = currentUser.specialty === 'ict-fachmann' ? areasIct : areasInformatiker;
    if (currentUser.specialty === 'ict-fachmann') {
      setAreas(allAreas);
    } else {
      setAreas(allAreas.filter(a => a.specialty === 'both' || a.specialty === currentUser.specialty));
    }
  }, [currentUserId, areasInformatiker, areasIct, currentUser]);

  const currentAP = ausbildungsplaetze.find(ap => ap.code === currentAPCode) ?? null;

  const activeAP = (() => {
    if (!currentUser?.rotations?.length) return null;
    const today = new Date().toISOString().split('T')[0];
    const rot = currentUser.rotations.find(r =>
      r.von <= today && (!r.bis || r.bis >= today)
    );
    return rot ? (ausbildungsplaetze.find(ap => ap.code === rot.ap_code) ?? null) : null;
  })();

  const selectAP = useCallback((code: string) => setCurrentAPCode(code), []);

  const updateApHk = useCallback(async (
    apCode: string, bildungsplan: string, hkId: string, coverage: string
  ) => {
    await api.updateApHk(apCode, bildungsplan, hkId, coverage);
    setAusbildungsplaetze(prev => prev.map(ap => {
      if (ap.code !== apCode) return ap;
      return {
        ...ap,
        hk_coverage: {
          ...ap.hk_coverage,
          [bildungsplan]: { ...ap.hk_coverage?.[bildungsplan], [hkId]: coverage },
        },
      };
    }));
  }, []);

  const addAusbildungsplatz = useCallback(async (body: Partial<Ausbildungsplatz>) => {
    const created = await api.createAusbildungsplatz(body);
    setAusbildungsplaetze(prev => [...prev, created]);
    setCurrentAPCode(created.code);
    return created;
  }, []);

  const addRotation = useCallback(async (userId: string, body: Partial<Rotation>) => {
    const created = await api.addRotation(userId, body);
    setUsers(prev => prev.map(u =>
      u.id === userId
        ? { ...u, rotations: [...(u.rotations ?? []), created].sort((a, b) => a.von.localeCompare(b.von)) }
        : u
    ));
    return created;
  }, []);

  const updateRotation = useCallback(async (userId: string, rotId: string, body: Partial<Rotation>) => {
    const updated = await api.updateRotation(userId, rotId, body);
    setUsers(prev => prev.map(u =>
      u.id === userId
        ? { ...u, rotations: u.rotations.map(r => r.id === rotId ? updated : r) }
        : u
    ));
    return updated;
  }, []);

  const deleteRotation = useCallback(async (userId: string, rotId: string) => {
    // Optimistisches Update: sofort aus UI entfernen, dann API aufrufen
    setUsers(prev => prev.map(u =>
      u.id === userId ? { ...u, rotations: u.rotations.filter(r => r.id !== rotId) } : u
    ));
    await api.deleteRotation(userId, rotId);
  }, []);

  const selectUser = useCallback((id: string) => setCurrentUserId(id), []);

  const reloadGoals = useCallback(async (userId: string) => {
    const goalList = await api.getGoals(userId).catch(() => []);
    setUsers(prev => prev.map(u => {
      if (u.id !== userId) return u;
      const goals: User['goals'] = {};
      goalList.forEach(g => {
        goals[g.goal_id] = {
          level:         g.effective_level as BloomLevel,
          manual_level:  g.manual_level as BloomLevel,
          comment:       g.comment ?? '',
          date:          g.updated_at ?? undefined,
          contributions: (g.document_contributions ?? []).map((c): GoalContribution => ({
            doc_id:      c.doc_id,
            doc_title:   c.doc_title,
            bloom_level: c.bloom_level,
          })),
        };
      });
      return { ...u, goals };
    }));
  }, []);

  const updateGoal = useCallback(async (goalId: string, level: BloomLevel, comment: string) => {
    if (!currentUser) return;
    await api.saveGoal(currentUser.id, goalId, { goal_id: goalId, level, comment });
    setUsers(prev => prev.map(u =>
      u.id !== currentUser.id ? u : {
        ...u,
        goals: {
          ...u.goals,
          [goalId]: {
            ...u.goals[goalId],
            level,
            manual_level: level,
            comment,
            date: new Date().toISOString(),
          },
        },
      }
    ));
  }, [currentUser]);

  const addUser = useCallback(async (body: Partial<User>) => {
    const created = await api.createUser(body);
    setUsers(prev => [...prev, { ...created, startDate: created.start_date, goals: {}, rotations: [] }]);
    return created;
  }, []);

  const editUser = useCallback(async (id: string, body: Partial<User>) => {
    const updated = await api.updateUser(id, body);
    setUsers(prev => prev.map(u =>
      u.id === id ? { ...u, ...updated, startDate: updated.start_date } : u
    ));
  }, []);

  const removeUser = useCallback(async (id: string) => {
    await api.deleteUser(id);
    setUsers(prev => prev.filter(u => u.id !== id));
    if (currentUserId === id) setCurrentUserId(null);
  }, [currentUserId]);

  useEffect(() => {
    if (!currentUserId) { setDocuments([]); return; }
    api.getDocuments(currentUserId).then(setDocuments).catch(() => setDocuments([]));
  }, [currentUserId]);

  const uploadDocument = useCallback(async (userId: string, formData: FormData) => {
    const created = await api.uploadDocument(userId, formData);
    setDocuments(prev => [created, ...prev]);
    return created;
  }, []);

  const updateDocument = useCallback(async (userId: string, docId: string, body: { title: string; description?: string; ap_code: string; goal_ids: string[]; kurzbeschreibung?: string; umsetzung?: string; luecken?: string; feedback_berufsbildner?: string; document_date?: string; }) => {
    const updated = await api.updateDocument(userId, docId, body);
    setDocuments(prev => prev.map(d => d.id === docId ? updated : d));
  }, []);

  const deleteDocument = useCallback(async (userId: string, docId: string) => {
    await api.deleteDocument(userId, docId);
    setDocuments(prev => prev.filter(d => d.id !== docId));
    await reloadGoals(userId);
  }, [reloadGoals]);

  const aiEvaluateDocument = useCallback(async (userId: string, docId: string) => {
    const res = await api.aiEvaluateDocument(userId, docId);
    setDocuments(prev => prev.map(d => d.id === docId ? res.document : d));
    await reloadGoals(userId);
    return res;
  }, [reloadGoals]);

  const updateDocumentGoal = useCallback(async (userId: string, docId: string, goalId: string, einschaetzung: string | null, bloomLevel: number | null) => {
    const updated = await api.updateDocumentGoal(userId, docId, goalId, { einschaetzung, bloom_level: bloomLevel });
    setDocuments(prev => prev.map(d => d.id === docId
      ? { ...d, goal_links: d.goal_links.map(l => l.goal_id === goalId ? { ...l, einschaetzung: updated.einschaetzung, bloom_level: updated.bloom_level } : l) }
      : d
    ));
    return updated;
  }, []);

  return (
    <AppContext.Provider value={{
      users, currentUser, areas, areasInformatiker, areasIct, loading, error, role, setRole,
      ausbildungsplaetze, currentAP, currentAPCode, selectAP, updateApHk, addAusbildungsplatz,
      activeAP,
      rotationGanttView, setRotationGanttView,
      selectUser, updateGoal, reloadGoals, addUser, editUser, removeUser,
      addRotation, updateRotation, deleteRotation,
      documents, uploadDocument, updateDocument, deleteDocument, updateDocumentGoal, aiEvaluateDocument,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp muss innerhalb von AppProvider verwendet werden');
  return ctx;
}

// Konstante bleibt exportiert, falls andere Module sie brauchen
export { COMPETENCY_FILE };
