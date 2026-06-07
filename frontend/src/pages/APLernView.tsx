import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import GoalRow from '../components/GoalRow';

const BLOOM_LABELS = ['–', 'Wissen', 'Verstehen', 'Anwenden', 'Analysieren', 'Synthese', 'Beurteilen'];
const BLOOM_COLORS = ['#94a3b8', '#60a5fa', '#34d399', '#a3e635', '#fbbf24', '#f97316', '#a855f7'];

export default function APLernView() {
  const { apCode }   = useParams<{ apCode: string }>();
  const navigate     = useNavigate();
  const { currentUser, areas, ausbildungsplaetze } = useApp();
  const [openAreas, setOpenAreas] = useState<Record<string, boolean>>({});
  const [openScs,   setOpenScs]   = useState<Record<string, boolean>>({});

  if (!currentUser) {
    navigate('/overview', { replace: true });
    return null;
  }

  const ap = ausbildungsplaetze.find(a => a.code === apCode);
  if (!ap) {
    return (
      <div className="no-user-state">
        <h3>Ausbildungsplatz nicht gefunden</h3>
        <button className="btn btn-secondary" onClick={() => navigate('/overview')}>← Zurück</button>
      </div>
    );
  }

  const bildungsplan = currentUser.specialty === 'ict-fachmann' ? 'ict-fachmann' : 'informatiker';
  const apCov = (ap.hk_coverage?.[bildungsplan] ?? {}) as Record<string, string>;

  const areasWithAP = areas
    .map(area => {
      const relevantScs = area.subComps.filter(
        sc => apCov[sc.id] === 'primary' || apCov[sc.id] === 'secondary'
      );
      const scAchieved    = relevantScs.filter(sc =>
        sc.goals.length > 0 && sc.goals.every(g => (currentUser.goals?.[g.id]?.level ?? 0) >= g.max)
      ).length;
      const totalGoals    = relevantScs.flatMap(sc => sc.goals).length;
      const ratedGoals    = relevantScs.flatMap(sc => sc.goals)
        .filter(g => (currentUser.goals?.[g.id]?.level ?? 0) > 0).length;
      const achievedGoals = relevantScs.flatMap(sc => sc.goals)
        .filter(g => (currentUser.goals?.[g.id]?.level ?? 0) >= g.max).length;
      return { area, relevantScs, scAchieved, totalGoals, ratedGoals, achievedGoals };
    })
    .filter(a => a.relevantScs.length > 0);

  const totalGoalsAll    = areasWithAP.reduce((s, a) => s + a.totalGoals,    0);
  const ratedGoalsAll    = areasWithAP.reduce((s, a) => s + a.ratedGoals,    0);
  const achievedGoalsAll = areasWithAP.reduce((s, a) => s + a.achievedGoals, 0);
  const pct = totalGoalsAll > 0 ? Math.round(achievedGoalsAll / totalGoalsAll * 100) : 0;

  return (
    <div className="area-view-page">

      {/* Header */}
      <div className="area-header">
        <button
          style={{ background: 'none', border: 'none', color: '#666', fontSize: '0.82rem', cursor: 'pointer', padding: 0, marginBottom: 6 }}
          onClick={() => navigate('/overview')}
        >
          ← Übersicht
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span className="ap-code-badge">{ap.code}</span>
          <h2 style={{ margin: 0 }}>Ausbildungsplatz {ap.name}</h2>
        </div>
        <div className="area-meta">
          {ratedGoalsAll} von {totalGoalsAll} Leistungszielen bewertet
        </div>
        <div className="area-progress-bar-wrap">
          <div className="area-progress-label">
            <span>Fortschritt</span>
            <span>{pct}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
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

      {/* Zweistufiges Accordion: Bereich → HK → Leistungsziele */}
      <div className="sub-comp-list" style={{ padding: '8px 24px 24px' }}>
        {areasWithAP.length === 0 ? (
          <div style={{ padding: '20px 0', color: '#888', fontSize: '0.88rem' }}>
            Für diesen Ausbildungsplatz sind noch keine Handlungskompetenzen hinterlegt.
          </div>
        ) : areasWithAP.map(({ area, relevantScs, scAchieved }) => {
          const areaOpen = openAreas[area.id] ?? false;
          return (
            <div key={area.id} className={`sub-comp${areaOpen ? ' open' : ''}`}>
              {/* Bereichs-Header */}
              <button className="sub-comp-header" onClick={() =>
                setOpenAreas(prev => ({ ...prev, [area.id]: !prev[area.id] }))
              }>
                <span className="sub-comp-id">{area.id.toUpperCase()}</span>
                <span className="sub-comp-name">{area.name}</span>
                <span className="sub-comp-stats">{scAchieved}/{relevantScs.length}</span>
                <span className="accordion-icon">{areaOpen ? '×' : '+'}</span>
              </button>

              {/* HK-Liste innerhalb des Bereichs */}
              <div className="sub-comp-body">
                {relevantScs.map(sc => {
                  const scOpen  = openScs[sc.id] ?? false;
                  const scDone  = sc.goals.filter(
                    g => (currentUser.goals?.[g.id]?.level ?? 0) >= g.max
                  ).length;
                  return (
                    <div key={sc.id} className={`sub-comp sub-comp-nested${scOpen ? ' open' : ''}`}>
                      <button className="sub-comp-header sub-comp-header-nested"
                        onClick={() => setOpenScs(prev => ({ ...prev, [sc.id]: !prev[sc.id] }))}>
                        <span className="sub-comp-id">{sc.id}</span>
                        <span className="sub-comp-name">{sc.name}</span>
                        <span className="sub-comp-stats">{scDone}/{sc.goals.length}</span>
                        <span className="accordion-icon">{scOpen ? '×' : '+'}</span>
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
        })}
      </div>

    </div>
  );
}
