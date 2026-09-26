import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getLehrjahrInfo, getAreaProgress, getOverallProgress, getAPLernProgress } from '../utils';
import { generatePDF } from '../utils/generatePDF';
import DonutChart from '../components/DonutChart';
import type { Ausbildungsplatz } from '../types';

const AREA_COLORS = [
  '#1d4ed8', '#0d9488', '#d97706', '#dc2626',
  '#7c3aed', '#db2777', '#059669', '#0891b2',
];

function progressEmoji(pct: number): string {
  if (pct >= 80) return '/IconEmoji_5.jpg';
  if (pct >= 60) return '/IconEmoji_4.jpg';
  if (pct >= 40) return '/IconEmoji_3.jpg';
  if (pct >= 20) return '/IconEmoji_2.jpg';
  return '/IconEmoji_1.png';
}

function MiniDonut({ pct, color }: { pct: number; color: string }) {
  const size = 34;
  const cx = size / 2, cy = size / 2;
  const r = size * 0.36;
  const strokeW = size * 0.20;
  const circ = 2 * Math.PI * r;
  const filled = (pct / 100) * circ;
  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', flexShrink: 0 }}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e4e8" strokeWidth={strokeW} />
      {pct > 0 && (
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={strokeW}
          strokeDasharray={`${filled} ${circ - filled}`} strokeLinecap="butt" />
      )}
    </svg>
  );
}

export default function Overview() {
  const { currentUser, areas, ausbildungsplaetze, documents } = useApp();
  const navigate = useNavigate();

  function goToTag(tag: string) {
    navigate(`/dokumente?tag=${encodeURIComponent(tag)}`);
  }

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

  const bildungsplan = currentUser.specialty === 'ict-fachmann' ? 'ict-fachmann'
                     : currentUser.specialty === 'betriebsinformatik' ? 'betriebsinformatik'
                     : 'informatiker';
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
      label:  `Handlungskompetenz ${p.area.id.toUpperCase()}: ${p.area.name}`,
      sub:    `${p.achieved}/${p.total} Leistungsziele (${p.pct}%)`,
      value:  p.achieved,
      color:  AREA_COLORS[i % AREA_COLORS.length],
      areaId: p.area.id as string | null,
      pct:    p.pct,
    })),
    {
      label:  'Noch nicht erreicht',
      sub:    `${notAchieved}/${totalGoals} (${totalGoals > 0 ? Math.round(notAchieved / totalGoals * 100) : 0}%)`,
      value:  notAchieved,
      color:  '#9ca3af',
      areaId: null,
      pct:    totalGoals > 0 ? Math.round(notAchieved / totalGoals * 100) : 0,
    },
  ];

  const ljTotal = yearPcts.reduce((s, p) => s + p, 0) / yearPcts.length;

  return (
    <div className="page-body">

      {/* Lehrzeit-Fortschritt */}
      <div className="section-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3>Lehrzeit-Fortschritt ({Math.round(ljTotal)}% absolviert)</h3>
          <button className="header-icon-btn" title="PDF-Bericht erstellen"
            onClick={() => generatePDF(currentUser, areas, documents)}>
            <img src="/IconPDF.png" style={{ height: '22px', display: 'block' }} alt="PDF" />
          </button>
        </div>
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
            <img src={progressEmoji(p.pct)} alt="" style={{ position: 'absolute', top: 6, right: 6, width: 36, height: 36, objectFit: 'contain' }} />
            <div className="ov-id">Handlungskompetenz {p.area.id.toUpperCase()}</div>
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

      {/* Pie-Chart / Gesamtfortschritt + Tech-Tags */}
      <div className="pie-section" style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 480px' }}>
        <div className="pie-title">Gesamtfortschritt der Leistungszielerreichung</div>
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
                  title={`Zu Handlungskompetenz ${seg.areaId.toUpperCase()} wechseln`}
                >
                  <MiniDonut pct={seg.pct} color={seg.color} />
                  <div className="pie-legend-text">
                    <div className="pie-legend-label">{seg.label}</div>
                    <div className="pie-legend-sub">{seg.sub}</div>
                  </div>
                  <span className="pie-legend-arrow">›</span>
                </button>
              ) : (
                <div key={i} className="pie-legend-item">
                  <MiniDonut pct={seg.pct} color={seg.color} />
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

        {/* Tech + System Chips */}
        {(() => {
          const techCount: Record<string, number> = {};
          const envCount:  Record<string, number> = {};
          for (const doc of documents) {
            for (const t of doc.technologies ?? []) techCount[t] = (techCount[t] ?? 0) + 1;
            for (const e of doc.environments  ?? []) envCount[e]  = (envCount[e]  ?? 0) + 1;
          }
          const techs = Object.entries(techCount).sort((a, b) => b[1] - a[1]);
          const envs  = Object.entries(envCount).sort((a, b) => b[1] - a[1]);
          if (techs.length === 0 && envs.length === 0) return null;
          return (
            <div style={{ flex: '1 1 400px', minWidth: 320 }}>
              <div className="pie-title">Technologien &amp; Systeme</div>
              {techs.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>Technologie</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {techs.map(([tag, count]) => (
                      <button key={tag} onClick={() => goToTag(tag)}
                        style={{ background: '#dbeafe', color: '#1e40af', borderRadius: 12, padding: '3px 10px', fontSize: 12, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', border: 'none' }}
                        title={`Dokumente mit «${tag}» anzeigen`}>
                        {tag}{count > 1 && <span style={{ opacity: 0.6, marginLeft: 4 }}>×{count}</span>}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {envs.length > 0 && (
                <div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>System / Umgebung</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {envs.map(([tag, count]) => (
                      <button key={tag} onClick={() => goToTag(tag)}
                        style={{ background: '#dcfce7', color: '#166534', borderRadius: 12, padding: '3px 10px', fontSize: 12, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', border: 'none' }}
                        title={`Dokumente mit «${tag}» anzeigen`}>
                        {tag}{count > 1 && <span style={{ opacity: 0.6, marginLeft: 4 }}>×{count}</span>}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })()}
      </div>

    </div>
  );
}
