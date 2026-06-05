import { useState } from 'react';
import { useApp } from '../context/AppContext';
import { getInitials, getOverallProgress, getLehrjahrInfo, SPECIALTY_LABEL } from '../utils';
import UserModal from './UserModal';
import type { User } from '../types';

export default function TopBar() {
  const { users, currentUser, areas, selectUser } = useApp();
  const [showPanel, setShowPanel] = useState(false);
  const [editUser,  setEditUser]  = useState<User | null>(null);
  const [showAdd,   setShowAdd]   = useState(false);

  const overall = currentUser ? getOverallProgress(areas, currentUser.goals) : null;
  const ljInfo  = currentUser ? getLehrjahrInfo(currentUser) : null;

  function openEdit(u: User, e: React.MouseEvent) {
    e.stopPropagation();
    setShowPanel(false);
    setEditUser(u);
  }

  return (
    <header className="topbar">
      <span className="topbar-title">Handlungskompetenz-Tracker</span>

      {currentUser && (
        <>
          <div className="topbar-user">
            <div className="user-avatar-lg">{getInitials(currentUser.name)}</div>
            <div className="topbar-user-info">
              <div className="name">{currentUser.name}</div>
              <div className="specialty">{SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty}</div>
            </div>
          </div>

          {ljInfo && <span className="lj-badge">{ljInfo.current}. Lehrjahr</span>}
          {overall && <span className="overall-pct-badge">{overall.pct}%</span>}

          <div className="topbar-divider" />
        </>
      )}

      <div style={{ position: 'relative' }}>
        <button className="topbar-btn" onClick={() => setShowPanel(p => !p)}>
          <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 8a3 3 0 100-6 3 3 0 000 6zm-5 6a5 5 0 0110 0H3z" />
          </svg>
          Wechseln
        </button>

        {showPanel && (
          <>
            <div className="user-panel-backdrop" onClick={() => setShowPanel(false)} />
            <div className="user-panel">
              <div className="user-panel-header">Lernende</div>
              <div className="user-panel-list">
                {users.map(u => (
                  <button
                    key={u.id}
                    className={`user-panel-item${currentUser?.id === u.id ? ' active' : ''}`}
                    onClick={() => { selectUser(u.id); setShowPanel(false); }}
                  >
                    <div className="up-avatar">{getInitials(u.name)}</div>
                    <div className="up-info">
                      <div className="up-name">{u.name}</div>
                      <div className="up-spec">{SPECIALTY_LABEL[u.specialty] ?? u.specialty}</div>
                    </div>
                    <span className="edit-icon" onClick={e => openEdit(u, e)}>✎</span>
                  </button>
                ))}
              </div>
              <div className="user-panel-footer">
                <button className="btn-add-user-panel" onClick={() => { setShowPanel(false); setShowAdd(true); }}>
                  + Lernende/n erfassen
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {editUser && <UserModal user={editUser} onClose={() => setEditUser(null)} />}
      {showAdd  && <UserModal onClose={() => setShowAdd(false)} />}
    </header>
  );
}
