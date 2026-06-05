import {
  createContext, useContext, useState, useEffect, useCallback,
  type ReactNode,
} from 'react';
import { api } from '../api/client';
import type {
  User, Area, Ausbildungsplatz, Rotation, Specialty, Role, BloomLevel,
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
  addUser:            (body: Partial<User>) => Promise<User>;
  editUser:           (id: string, body: Partial<User>) => Promise<void>;
  removeUser:         (id: string) => Promise<void>;
  addRotation:        (userId: string, body: Partial<Rotation>) => Promise<Rotation>;
  updateRotation:     (userId: string, rotId: string, body: Partial<Rotation>) => Promise<Rotation>;
  deleteRotation:     (userId: string, rotId: string) => Promise<void>;
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
              goals[g.goal_id] = { level: g.level as unknown as BloomLevel, comment: g.comment ?? '', date: g.updated_at };
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

  const updateGoal = useCallback(async (goalId: string, level: BloomLevel, comment: string) => {
    if (!currentUser) return;
    await api.saveGoal(currentUser.id, goalId, { goal_id: goalId, level, comment });
    setUsers(prev => prev.map(u =>
      u.id === currentUser.id
        ? { ...u, goals: { ...u.goals, [goalId]: { level, comment, date: new Date().toISOString() } } }
        : u
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

  return (
    <AppContext.Provider value={{
      users, currentUser, areas, areasInformatiker, areasIct, loading, error, role, setRole,
      ausbildungsplaetze, currentAP, currentAPCode, selectAP, updateApHk, addAusbildungsplatz,
      activeAP,
      rotationGanttView, setRotationGanttView,
      selectUser, updateGoal, addUser, editUser, removeUser,
      addRotation, updateRotation, deleteRotation,
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
