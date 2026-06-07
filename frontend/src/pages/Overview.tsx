import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getLehrjahrInfo, getAreaProgress, getOverallProgress, getAPLernProgress } from '../utils';
import DonutChart from '../components/DonutChart';
import type { Ausbildungsplatz } from '../types';

const AREA_COLORS = [
  '#1d4ed8', '#0d9488', '#d97706', '#dc2626',
  '#7c3aed', '#db2777', '#059669', '#0891b2',
];

export default function Overview() {
  const { currentUser, areas, ausbildungsplaetze, documents } = useApp();
  const navigate = useNavigate();

  if (!currentUser) {
    return (
      <div className="no-user-state">
        <h3>Kein/e Lernende/r ausgewählt</h3>
        <p>Klicke oben auf «Wechseln» um eine Person auszuwählen oder zu erfassen.</p>
      </div>
    );
  }

  const { yearPcts } = getLehrjahrInfo(currentUser);
  const overall = getOverallProgress(areas, currentUser.goals);

  const bildungsplan = currentUser.specialty === 'ict-fachmann' ? 'ict-fachmann' : 'informatiker';
  const uniqueApCodes = [...new Set(currentUser.rotations.map(r => r.ap_code))];
  const learnerAPs = uniqueApCodes
    .map(code => ausbildungsplaetze.find(ap => ap.code === code))
    .filter((ap): ap is Ausbildungsplatz => !!ap && (ap.abLehrjahr ?? 2) > 1);

  const areaProgs = areas.map((area, i) => ({
    ...getAreaProgress(area, currentUser.goals),
    area,
    color: AREA_COLORS[i % AREA_COLORS.length],
  }));

  const totalGoals    = areaProgs.reduce((s, p) => s + p.total,    0);
  const totalAchieved = areaProgs.reduce((s, p) => s + p.achieved, 0);
  const notAchieved   = totalGoals - totalAchieved;

  const pieSegments = [
    ...areaProgs.map((p, i) => ({
      label:  `Bereich ${p.area.id.toUpperCase()}: ${p.area.name}`,
      sub:    `${p.achieved}/${p.total} Leistungsziele (${p.pct}%)`,
      value:  p.achieved,
      color:  AREA_COLORS[i % AREA_COLORS.length],
      areaId: p.area.id as string | null,
    })),
    {
      label:  'Noch nicht erreicht',
      sub:    `${notAchieved}/${totalGoals} (${totalGoals > 0 ? Math.round(notAchieved / totalGoals * 100) : 0}%)`,
      value:  notAchieved,
      color:  '#e2e4e8',
      areaId: null,
    },
  ];

  const ljTotal = yearPcts.reduce((s, p) => s + p, 0) / yearPcts.length;

  return (
    <div className="page-body">

      {/* Lehrzeit-Fortschritt */}
      <div className="section-card">
        <h3>Lehrzeit-Fortschritt ({Math.round(ljTotal)}% absolviert)</h3>
        <div className="lehrzeit-bars">
          {yearPcts.map((pct, i) => {
            const cls = pct === 100 ? 'lj-done' : pct > 0 ? 'lj-current' : '';
            return (
              <div key={i} className="lj-col">
                <div className="lj-label">{i + 1}. LJ</div>
                <div className="lj-bar">
                  <div className={`lj-fill ${cls}`} style={{ width: `${pct}%` }} />
                </div>
                <div className="lj-pct">{pct}%</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bereichs-Kacheln */}
      <div className="area-cards-row">
        {areaProgs.map((p, i) => (
          <button
            key={p.area.id}
            className="overview-card"
            onClick={() => navigate(`/area/${p.area.id}`)}
          >
            <div className="ov-id">Bereich {p.area.id.toUpperCase()}</div>
            <div className="ov-name">{p.area.name}</div>
            <div className="ov-progress-bar">
              <div
                className="ov-progress-fill"
                style={{ width: `${p.pct}%`, background: `linear-gradient(90deg, ${AREA_COLORS[i % AREA_COLORS.length]}, ${AREA_COLORS[i % AREA_COLORS.length]}aa)` }}
              />
            </div>
            <div className="ov-pct">{p.achieved}/{p.total} Leistungsziele ({p.pct}%)</div>
          </button>
        ))}
      </div>

      {/* Ausbildungsplatz-Kacheln */}
      {learnerAPs.length > 0 && (
        <div className="area-cards-row">
          {learnerAPs.map(ap => {
            const apCoverage = (ap.hk_coverage?.[bildungsplan] ?? {}) as Record<string, string>;
            const prog     = getAPLernProgress(apCoverage, areas, currentUser.goals);
            const docCount = documents.filter(d => d.ap_code === ap.code).length;
            return (
              <button key={ap.code} className="overview-card" onClick={() => navigate('/dokumente')}>
                <div className="ov-id">Ausbildungsplatz: {ap.code}</div>
                <div className="ov-name">{ap.name}</div>
                <div className="ov-progress-bar">
                  <div className="ov-progress-fill" style={{ width: `${prog.pct}%` }} />
                </div>
                <div className="ov-pct">{prog.achieved}/{prog.total} Leistungsziele ({prog.pct}%)</div>
                <div className="ov-doc-count">Hochgeladene Dokumente: {docCount}</div>
              </button>
            );
          })}
        </div>
      )}

      {/* Pie-Chart / Gesamtfortschritt */}
      <div className="pie-section">
        <div className="pie-title">Gesamtfortschritt / Leistungszielerreichung</div>
        <div className="pie-layout">
          <div className="pie-chart-wrap">
            <DonutChart segments={pieSegments} centerPct={overall.pct} />
          </div>
          <div className="pie-legend">
            {pieSegments.map((seg, i) =>
              seg.areaId ? (
                <button
                  key={i}
                  className="pie-legend-item pie-legend-link"
                  onClick={() => navigate(`/area/${seg.areaId}`)}
                  title={`Zu Bereich ${seg.areaId.toUpperCase()} wechseln`}
                >
                  <div className="pie-legend-dot" style={{ background: seg.color }} />
                  <div className="pie-legend-text">
                    <div className="pie-legend-label">{seg.label}</div>
                    <div className="pie-legend-sub">{seg.sub}</div>
                  </div>
                  <span className="pie-legend-arrow">›</span>
                </button>
              ) : (
                <div key={i} className="pie-legend-item">
                  <div className="pie-legend-dot" style={{ background: seg.color }} />
                  <div className="pie-legend-text">
                    <div className="pie-legend-label">{seg.label}</div>
                    <div className="pie-legend-sub">{seg.sub}</div>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </div>

    </div>
  );
}
