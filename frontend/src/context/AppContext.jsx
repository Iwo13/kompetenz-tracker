import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

const AppContext = createContext(null);

const COMPETENCY_FILE = {
  'platform':     'kompetenzen-informatiker-efz',
  'app':          'kompetenzen-informatiker-efz',
  'ict-fachmann': 'kompetenzen-ict-fachmann-efz',
};

export function AppProvider({ children }) {
  const [users, setUsers]               = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [areas, setAreas]               = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);

  // Beim Start: Users + beide Kompetenz-JSONs laden
  const [areasInformatiker, setAreasInformatiker] = useState([]);
  const [areasIct, setAreasIct]                   = useState([]);

  useEffect(() => {
    async function init() {
      try {
        const [compInfo, compIct, userList] = await Promise.all([
          api.getCompetencies('kompetenzen-informatiker-efz'),
          api.getCompetencies('kompetenzen-ict-fachmann-efz'),
          api.getUsers(),
        ]);
        setAreasInformatiker(compInfo.areas);
        setAreasIct(compIct.areas);

        // Goals für alle User laden
        const usersWithGoals = await Promise.all(
          userList.map(async (u) => {
            const goalList = await api.getGoals(u.id).catch(() => []);
            const goals = {};
            goalList.forEach(g => {
              goals[g.goal_id] = { level: g.level, comment: g.comment || '', date: g.updated_at };
            });
            return { ...u, startDate: u.start_date, goals };
          })
        );
        setUsers(usersWithGoals);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Aktuelle Areas abhängig vom User
  const currentUser = users.find(u => u.id === currentUserId) ?? null;

  useEffect(() => {
    if (!currentUser) return;
    const allAreas = currentUser.specialty === 'ict-fachmann' ? areasIct : areasInformatiker;
    if (currentUser.specialty === 'ict-fachmann') {
      setAreas(allAreas);
    } else {
      setAreas(allAreas.filter(a => a.specialty === 'both' || a.specialty === currentUser.specialty));
    }
  }, [currentUserId, areasInformatiker, areasIct]);

  const selectUser = useCallback((id) => setCurrentUserId(id), []);

  const updateGoal = useCallback(async (goalId, level, comment) => {
    if (!currentUser) return;
    await api.saveGoal(currentUser.id, { goal_id: goalId, level, comment });
    setUsers(prev => prev.map(u =>
      u.id === currentUser.id
        ? { ...u, goals: { ...u.goals, [goalId]: { level, comment, date: new Date().toISOString() } } }
        : u
    ));
  }, [currentUser]);

  const addUser = useCallback(async (body) => {
    const created = await api.createUser(body);
    setUsers(prev => [...prev, { ...created, startDate: created.start_date, goals: {} }]);
    return created;
  }, []);

  const editUser = useCallback(async (id, body) => {
    const updated = await api.updateUser(id, body);
    setUsers(prev => prev.map(u =>
      u.id === id ? { ...u, ...updated, startDate: updated.start_date } : u
    ));
  }, []);

  const removeUser = useCallback(async (id) => {
    await api.deleteUser(id);
    setUsers(prev => prev.filter(u => u.id !== id));
    if (currentUserId === id) setCurrentUserId(null);
  }, [currentUserId]);

  return (
    <AppContext.Provider value={{
      users, currentUser, areas, loading, error,
      selectUser, updateGoal, addUser, editUser, removeUser,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
