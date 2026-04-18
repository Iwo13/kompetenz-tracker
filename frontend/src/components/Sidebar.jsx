import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getAreaProgress, SPECIALTY_LABEL } from '../utils';

export default function Sidebar() {
  const { currentUser, areas } = useApp();
  const navigate  = useNavigate();
  const location  = useLocation();
  const isOverview = location.pathname === '/overview' || location.pathname === '/';

  return (
    <aside className="sidebar">
      {/* App-Titel */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-title">Handlungskompetenz-<br />Tracker</div>
        <div className="sidebar-brand-sub">
          {currentUser
            ? (SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty)
            : 'Informatik EFZ'}
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">Navigation</div>
        <button
          className={`sidebar-item${isOverview ? ' active' : ''}`}
          onClick={() => navigate('/overview')}
        >
          <span className="item-id">
            <img src="/IconBuch.png" style={{ height: '16px', width: '16px', objectFit: 'contain', display: 'block' }} alt="" />
          </span>
          <span className="item-name">Übersicht</span>
        </button>
      </div>

      {/* Bereiche */}
      {areas.length > 0 && (
        <div className="sidebar-section">
          <div className="sidebar-section-title">Bereiche</div>
          {areas.map(area => {
            const prog    = getAreaProgress(area, currentUser?.goals);
            const isActive = location.pathname === `/area/${area.id}`;
            return (
              <button
                key={area.id}
                className={`sidebar-item${isActive ? ' active' : ''}`}
                onClick={() => navigate(`/area/${area.id}`)}
              >
                <span className="item-id">{area.id.toUpperCase()}</span>
                <span className="item-name">{area.name}</span>
                <span className={`item-badge${prog.pct === 100 ? ' done' : ''}`}>
                  {prog.pct}%
                </span>
              </button>
            );
          })}
        </div>
      )}
    </aside>
  );
}
