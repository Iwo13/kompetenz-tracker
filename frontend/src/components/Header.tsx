import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getInitials, getOverallProgress, getLehrjahrInfo, SPECIALTY_LABEL } from '../utils';
import { generatePDF } from '../utils/generatePDF';
import UserModal from './UserModal';
import APModal from './APModal';
import type { User } from '../types';

function PersonIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 12c2.67 0 8 1.34 8 4v2H4v-2c0-2.66 5.33-4 8-4zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
    </svg>
  );
}

interface HeaderProps {
  onToggleSidebar: () => void;
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const {
    users, currentUser, areas, selectUser, role, setRole,
    ausbildungsplaetze, currentAP, activeAP, selectAP, rotationGanttView,
  } = useApp();
  const location  = useLocation();
  const navigate  = useNavigate();
  const isAPView  = location.pathname.startsWith('/ap-abdeckung') ||
    (location.pathname === '/rotationsplanung' && rotationGanttView === 'ausbildungsplaetze');

  const [showLearnerPanel, setShowLearnerPanel] = useState(false);
  const [showAPPanel,      setShowAPPanel]      = useState(false);
  const [showProfilePanel, setShowProfilePanel] = useState(false);
  const [editUser,  setEditUser]  = useState<User | null>(null);
  const [showAdd,   setShowAdd]   = useState(false);
  const [showAddAP, setShowAddAP] = useState(false);

  const overall = currentUser ? getOverallProgress(areas, currentUser.goals) : null;
  const ljInfo  = currentUser ? getLehrjahrInfo(currentUser) : null;
  const pct     = overall?.pct ?? 0;
  const r = 14, circ = 2 * Math.PI * r;
  const isBB = role === 'berufsbildner';

  function openEdit(u: User, e: React.MouseEvent) {
    e.stopPropagation();
    setShowLearnerPanel(false);
    setEditUser(u);
  }
  function switchUser(id: string) {
    selectUser(id);
    setShowLearnerPanel(false);
    setShowProfilePanel(false);
  }

  const learnerList = (
    <>
      <div className="user-panel-list">
        {users.map(u => (
          <button key={u.id}
            className={`user-panel-item${currentUser?.id === u.id ? ' active' : ''}`}
            onClick={() => switchUser(u.id)}>
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
        <button className="btn-add-user-panel"
          onClick={() => { setShowLearnerPanel(false); setShowProfilePanel(false); setShowAdd(true); }}>
          + Lernende/n erfassen
        </button>
      </div>
    </>
  );

  const apList = (
    <>
      <div className="user-panel-list">
        {ausbildungsplaetze.map(ap => (
          <button key={ap.code}
            className={`user-panel-item${currentAP?.code === ap.code ? ' active' : ''}`}
            onClick={() => { selectAP(ap.code); setShowAPPanel(false); }}>
            <div className="up-avatar ap-avatar">{ap.code.substring(0, 3)}</div>
            <div className="up-info">
              <div className="up-name">{ap.code}</div>
              <div className="up-spec">{ap.name}</div>
            </div>
          </button>
        ))}
      </div>
      <div className="user-panel-footer">
        <button className="btn-add-user-panel"
          onClick={() => { setShowAPPanel(false); setShowAddAP(true); }}>
          + Ausbildungsplatz erfassen
        </button>
      </div>
    </>
  );

  return (
    <header className="header">
      <button className="hamburger" onClick={onToggleSidebar} aria-label="Menü öffnen">☰</button>

      <div className="header-logo-wrap">
        <img src="/FHNW_Logo.webp" alt="FHNW Nordwestschweiz" />
      </div>

      {/* Fallback-Titel (nur wenn kein User/AP) */}
      {!currentUser && !isAPView && (
        <div className="header-title">
          <span className="header-title-name">Handlungskompetenz-Tracker</span>
        </div>
      )}

      {/* Lernenden-Dropdown (Desktop + Mobile) */}
      {!isAPView && (
        <div className="header-name-area">
          <div className="learner-anchor">
            {currentUser ? (
              <button className="learner-btn"
                onClick={() => isBB && setShowLearnerPanel(p => !p)}
                style={{ cursor: isBB ? 'pointer' : 'default' }}>
                <div className="learner-btn-info">
                  <span className="learner-name">{currentUser.name}</span>
                  {activeAP && <span className="learner-btn-ap">{activeAP.code} – {activeAP.name}</span>}
                </div>
                {isBB && <span className="learner-caret">▾</span>}
              </button>
            ) : isBB ? (
              <button className="learner-btn learner-btn-empty"
                onClick={() => setShowLearnerPanel(p => !p)}>
                Lernende/n auswählen ▾
              </button>
            ) : null}
            {showLearnerPanel && isBB && (
              <>
                <div className="user-panel-backdrop" onClick={() => setShowLearnerPanel(false)} />
                <div className="user-panel learner-panel">
                  <div className="user-panel-header">Lernende</div>
                  {learnerList}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* AP-Dropdown (Desktop + Mobile) */}
      {isAPView && (
        <div className="header-name-area">
          <div className="learner-anchor">
            <button className="learner-btn" onClick={() => setShowAPPanel(p => !p)}>
              <div className="learner-btn-info">
                <span className="learner-name">{currentAP?.code ?? 'AP wählen'}</span>
                {currentAP && <span className="learner-btn-ap">{currentAP.name}</span>}
              </div>
              <span className="learner-caret">▾</span>
            </button>
            {showAPPanel && (
              <>
                <div className="user-panel-backdrop" onClick={() => setShowAPPanel(false)} />
                <div className="user-panel learner-panel">
                  <div className="user-panel-header">Ausbildungsplätze</div>
                  {apList}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Specialty / AP-Name zentriert */}
      <div className="header-center hide-mobile">
        {!isAPView && currentUser && (
          <div className="header-center-stack">
            <span className="header-specialty">
              {SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty}
            </span>
            {activeAP && (
              <span className="header-ap-label">{activeAP.code} – {activeAP.name}</span>
            )}
          </div>
        )}
        {isAPView && currentAP && (
          <span className="header-specialty">{currentAP.name}</span>
        )}
      </div>

      {/* Rechte Gruppe */}
      <div className="header-right">
        {!isAPView && currentUser && ljInfo && (
          <span className="lehrjahr-badge hide-mobile">{ljInfo.current}. Lehrjahr</span>
        )}
        {!isAPView && currentUser && (
          <div className="progress-ring-wrap hide-mobile" title={`${pct}% erreicht`}>
            <svg width="40" height="40">
              <circle cx="20" cy="20" r={r} fill="none" stroke="rgba(0,0,0,.15)" strokeWidth="4" />
              <circle cx="20" cy="20" r={r} fill="none"
                stroke="var(--fhnw-dark)" strokeWidth="4"
                strokeDasharray={`${pct / 100 * circ} ${circ}`}
                strokeLinecap="round"
                style={{ transform: 'rotate(-90deg)', transformOrigin: '20px 20px' }}
              />
            </svg>
            <div className="progress-ring-value">{pct}%</div>
          </div>
        )}

        <div className="header-sep hide-mobile" />

        {/* Profil-Dropdown */}
        <div className="user-panel-anchor">
          <button className="header-btn profile-btn"
            onClick={() => setShowProfilePanel(p => !p)} title="Profil & Ansicht">
            <PersonIcon /><span className="profile-btn-caret">▾</span>
          </button>
          {showProfilePanel && (
            <>
              <div className="user-panel-backdrop" onClick={() => setShowProfilePanel(false)} />
              <div className="user-panel">
                <div className="user-panel-header">Ansicht</div>
                <div className="role-toggle-section">
                  <button className={`role-chip${role === 'berufsbildner' ? ' active' : ''}`}
                    onClick={() => { setRole('berufsbildner'); setShowProfilePanel(false); }}>Berufsbildner/in</button>
                  <button className={`role-chip${role === 'lernender' ? ' active' : ''}`}
                    onClick={() => {
                      setRole('lernender');
                      setShowProfilePanel(false);
                      if (isAPView) navigate('/overview');
                    }}>Lernende/r</button>
                </div>
              </div>
            </>
          )}
        </div>

        {!isAPView && (
          <button className="header-icon-btn" title="PDF-Bericht erstellen"
            onClick={() => generatePDF(currentUser, areas)} disabled={!currentUser}>
            <img src="/IconPDF.png" style={{ height: '22px', display: 'block' }} alt="PDF" />
          </button>
        )}
      </div>

      {editUser  && <UserModal user={editUser} onClose={() => setEditUser(null)} />}
      {showAdd   && <UserModal onClose={() => setShowAdd(false)} />}
      {showAddAP && <APModal onClose={() => setShowAddAP(false)} />}
    </header>
  );
}
