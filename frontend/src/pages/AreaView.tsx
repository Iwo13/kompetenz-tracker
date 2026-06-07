import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getAreaProgress } from '../utils';
import GoalRow from '../components/GoalRow';

const BLOOM_LABELS = ['–', 'Wissen', 'Verstehen', 'Anwenden', 'Analysieren', 'Synthese', 'Beurteilen'];
const BLOOM_COLORS = ['#94a3b8', '#60a5fa', '#34d399', '#a3e635', '#fbbf24', '#f97316', '#a855f7'];

export default function AreaView() {
  const { areaId }  = useParams<{ areaId: string }>();
  const navigate    = useNavigate();
  const { currentUser, areas } = useApp();
  const [openScId, setOpenScId] = useState<string | null>(null);

  if (!currentUser) {
    navigate('/overview', { replace: true });
    return null;
  }

  const area = areas.find(a => a.id === areaId);
  if (!area) {
    return (
      <div className="no-user-state">
        <h3>Bereich nicht gefunden</h3>
        <button className="btn btn-secondary" onClick={() => navigate('/overview')}>← Zurück</button>
      </div>
    );
  }

  const prog = getAreaProgress(area, currentUser.goals);

  function toggleSc(scId: string) {
    setOpenScId(prev => prev === scId ? null : scId);
  }

  return (
    <div className="area-view-page">
      <div className="area-header">
        <span className="area-id">Kompetenzbereich {area.id.toUpperCase()}</span>
        <h2>{area.name}</h2>
        <div className="area-meta">{area.subComps.length} Handlungskompetenzen · {prog.total} Leistungsziele</div>
        <div className="area-progress-bar-wrap">
          <div className="area-progress-label">
            <span>{prog.achieved} von {prog.total} Leistungszielen erreicht</span>
            <span>{prog.pct}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${prog.pct}%` }} />
          </div>
        </div>
      </div>

      {/* Bloom-Legende */}
      <div className="bloom-legend">
        {BLOOM_LABELS.slice(1).map((label, i) => (
          <div key={i} className="bloom-item">
            <div className="bloom-dot" style={{ background: BLOOM_COLORS[i + 1] }} />
            <span>K{i + 1}: {label}</span>
          </div>
        ))}
      </div>

      {/* Accordion */}
      <div className="sub-comp-list" style={{ padding: '8px 24px 24px' }}>
        {area.subComps.map(sc => {
          const isOpen  = openScId === sc.id;
          const scTotal = sc.goals.length;
          const scDone  = sc.goals.filter(
            g => (currentUser.goals?.[g.id]?.level ?? 0) >= g.max
          ).length;

          return (
            <div key={sc.id} className={`sub-comp${isOpen ? ' open' : ''}`}>
              <button className="sub-comp-header" onClick={() => toggleSc(sc.id)}>
                <span className="sub-comp-id">{sc.id.toUpperCase()}</span>
                <span className="sub-comp-name">{sc.name}</span>
                <span className="sub-comp-stats">{scDone}/{scTotal}</span>
                <span className="accordion-icon">{isOpen ? '×' : '+'}</span>
              </button>
              <div className="sub-comp-body">
                {sc.goals.map(goal => (
                  <GoalRow key={goal.id} goal={goal} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
