import { useState } from 'react';
import { useApp } from '../context/AppContext';
import { getInitials, getOverallProgress, getLehrjahrInfo, SPECIALTY_LABEL } from '../utils';
import UserModal from './UserModal';

export default function Header() {
  const { users, currentUser, areas, selectUser } = useApp();
  const [showPanel, setShowPanel] = useState(false);
  const [editUser,  setEditUser]  = useState(null);
  const [showAdd,   setShowAdd]   = useState(false);

  const overall = currentUser ? getOverallProgress(areas, currentUser.goals) : null;
  const ljInfo  = currentUser ? getLehrjahrInfo(currentUser) : null;
  const pct     = overall?.pct ?? 0;
  const r = 14, circ = 2 * Math.PI * r;

  function openEdit(u, e) {
    e.stopPropagation();
    setShowPanel(false);
    setEditUser(u);
  }

  return (
    <header className="header">
      {/* Logo-Bereich (gleiche Breite wie Sidebar) */}
      <div className="header-logo-wrap">
        <img src="/FHNW_Logo.webp" alt="FHNW Nordwestschweiz" />
      </div>

      {/* Titel */}
      <span className="header-title">Handlungskompetenz-Tracker</span>

      {/* User-Info */}
      {currentUser && (
        <div className="header-user">
          <div className="avatar">{getInitials(currentUser.name)}</div>
          <div className="user-info">
            <div className="user-name">{currentUser.name}</div>
            <div className="user-detail">{SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty}</div>
          </div>
        </div>
      )}

      {/* Rechte Seite */}
      <div className="header-right">
        {currentUser && ljInfo && (
          <span className="lehrjahr-badge">{ljInfo.current}. Lehrjahr</span>
        )}

        {currentUser && (
          <div className="progress-ring-wrap" title={`${pct}% erreicht`}>
            <svg width="36" height="36">
              <circle cx="18" cy="18" r={r} fill="none" stroke="rgba(0,0,0,.15)" strokeWidth="4" />
              <circle
                cx="18" cy="18" r={r} fill="none"
                stroke="var(--fhnw-dark)" strokeWidth="4"
                strokeDasharray={`${pct / 100 * circ} ${circ}`}
                strokeLinecap="round"
              />
            </svg>
            <div className="progress-ring-value">{pct}%</div>
          </div>
        )}

        {/* Wechseln */}
        <div className="user-panel-anchor">
          <button className="header-btn" onClick={() => setShowPanel(p => !p)}>
            👤 Wechseln
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
                  <button
                    className="btn-add-user-panel"
                    onClick={() => { setShowPanel(false); setShowAdd(true); }}
                  >
                    + Lernende/n erfassen
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* PDF-Icon */}
        <button className="header-icon-btn" title="PDF-Bericht erstellen">
          <img src="/IconPDF.png" style={{ height: '22px', display: 'block' }} alt="PDF" />
        </button>
      </div>

      {editUser && <UserModal user={editUser} onClose={() => setEditUser(null)} />}
      {showAdd  && <UserModal onClose={() => setShowAdd(false)} />}
    </header>
  );
}
