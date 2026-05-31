import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import type { Area, Ausbildungsplatz } from '../types';

function calcCoverage(
  ap: Ausbildungsplatz | null,
  bildungsplan: string,
  hkIds: string[]
): { covered: number; total: number; pct: number } {
  if (!ap?.hk_coverage?.[bildungsplan] || hkIds.length === 0)
    return { covered: 0, total: hkIds.length, pct: 0 };
  const cov     = ap.hk_coverage[bildungsplan];
  const covered = hkIds.filter(id => cov[id] === 'primary').length;
  return { covered, total: hkIds.length, pct: Math.round(covered / hkIds.length * 100) };
}

export default function APAbdeckungOverview() {
  const { currentAP, areasInformatiker, areasIct } = useApp();
  const navigate = useNavigate();

  if (!currentAP) return (
    <div className="no-user-state">
      <h3>Kein Ausbildungsplatz ausgewählt</h3>
      <p>Klicke oben auf den AP-Dropdown um einen Ausbildungsplatz zu wählen.</p>
    </div>
  );

  function getHks(areas: Area[], fachrichtung: string | null) {
    return areas
      .filter(a => !fachrichtung || a.specialty === 'both' || a.specialty === fachrichtung)
      .flatMap(a => a.subComps.map(sc => sc.id));
  }

  const cards = [
    {
      key:          'informatiker-platform',
      label:        'Informatiker/in Plattformentwicklung',
      bildungsplan: 'informatiker',
      hkIds:        getHks(areasInformatiker, 'platform'),
      path:         '/ap-abdeckung/informatiker-platform',
    },
    {
      key:          'informatiker-app',
      label:        'Informatiker/in Applikationsentwicklung',
      bildungsplan: 'informatiker',
      hkIds:        getHks(areasInformatiker, 'app'),
      path:         '/ap-abdeckung/informatiker-app',
    },
    {
      key:          'ict-fachmann',
      label:        'ICT-Fachmann/frau',
      bildungsplan: 'ict-fachmann',
      hkIds:        getHks(areasIct, null),
      path:         '/ap-abdeckung/ict-fachmann',
    },
  ];

  return (
    <div className="page-body">
      <div className="ap-overview-cards">
        {cards.map(card => {
          const { covered, total, pct } = calcCoverage(currentAP, card.bildungsplan, card.hkIds);
          return (
            <button key={card.key} className="ap-overview-card"
              onClick={() => navigate(card.path)}>
              <div className="ap-ov-label">{card.label}</div>
              <div className="ap-ov-bar-wrap">
                <div className="ap-ov-bar">
                  <div className="ap-ov-bar-fill" style={{ width: `${pct}%` }} />
                </div>
              </div>
              <div className="ap-ov-stats">{covered} / {total}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
