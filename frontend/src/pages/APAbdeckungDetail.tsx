import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import type { Area } from '../types';

type CoverageValue = 'primary' | 'secondary' | null;
const COVERAGE_CYCLE: Record<string, CoverageValue> = {
  null:      'secondary',
  secondary: 'primary',
  primary:   null,
};
function nextCoverage(v: CoverageValue): CoverageValue {
  return COVERAGE_CYCLE[v ?? 'null'] ?? null;
}

function CoverageIcon({ value }: { value: CoverageValue }) {
  if (value === 'primary')   return <span className="hk-icon hk-primary">●</span>;
  if (value === 'secondary') return <span className="hk-icon hk-secondary">◐</span>;
  return <span className="hk-icon hk-none">○</span>;
}

interface AreaRowProps {
  area:         Area;
  bildungsplan: string;
  apCode:       string;
  coverage:     Record<string, string>;
  onToggle:     (hkId: string) => void;
}

function AreaRow({ area, coverage, onToggle }: AreaRowProps) {
  const [open, setOpen] = useState(false);

  const primaryCount = area.subComps.filter(sc => coverage[sc.id] === 'primary').length;
  const total        = area.subComps.length;

  return (
    <div className={`acc-block${open ? ' acc-open' : ''}`}>
      <button className="acc-header" onClick={() => setOpen(o => !o)}>
        <span className="acc-area-id">{area.id.toUpperCase()}</span>
        <span className="acc-area-name">{area.name}</span>
        {area.specialty && area.specialty !== 'both' && (
          <span className="acc-area-specialty">
            {area.specialty === 'platform' ? 'Plattformentwicklung' : 'Applikationsentwicklung'}
          </span>
        )}
        <span className="acc-count">{primaryCount} / {total}</span>
        <span className="acc-toggle">{open ? '×' : '+'}</span>
      </button>

      {open && (
        <div className="acc-body">
          {area.subComps.map(sc => (
            <div key={sc.id} className="hk-row" onClick={() => onToggle(sc.id)}>
              <span className="hk-id">{sc.id}</span>
              <span className="hk-name">{sc.name}</span>
              <CoverageIcon value={(coverage[sc.id] as CoverageValue) ?? null} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function APAbdeckungDetail() {
  const { bildungsplanKey } = useParams<{ bildungsplanKey: string }>();
  const { currentAP, areasInformatiker, areasIct, updateApHk } = useApp();
  const [savingKey, setSavingKey] = useState<string | null>(null);

  if (!currentAP) return (
    <div className="no-user-state">
      <h3>Kein Ausbildungsplatz ausgewählt</h3>
    </div>
  );

  let bildungsplan: string;
  let areas: Area[];
  let fachrichtungFilter: string | null;
  let pageTitle: string;
  let summaryRows: { label: string; hkIds: string[] }[];

  if (bildungsplanKey === 'ict-fachmann') {
    bildungsplan       = 'ict-fachmann';
    areas              = areasIct;
    fachrichtungFilter = null;
    pageTitle          = 'Bildungsplan ICT-Fachmann/frau EFZ';
    summaryRows        = [{ label: 'ICT-Fachmann/frau', hkIds: areasIct.flatMap(a => a.subComps.map(s => s.id)) }];
  } else {
    bildungsplan       = 'informatiker';
    fachrichtungFilter = bildungsplanKey === 'informatiker-platform' ? 'platform' : 'app';
    areas              = areasInformatiker.filter(a => a.specialty === 'both' || a.specialty === fachrichtungFilter);
    pageTitle          = 'Bildungsplan Informatiker/in EFZ';
    const pltHks = areasInformatiker.filter(a => a.specialty === 'both' || a.specialty === 'platform').flatMap(a => a.subComps.map(s => s.id));
    const appHks = areasInformatiker.filter(a => a.specialty === 'both' || a.specialty === 'app').flatMap(a => a.subComps.map(s => s.id));
    summaryRows = [
      { label: 'Plattformentwicklung',    hkIds: pltHks },
      { label: 'Applikationsentwicklung', hkIds: appHks },
    ];
  }

  const coverage = (currentAP.hk_coverage?.[bildungsplan] ?? {}) as Record<string, string>;

  function calcSummary(hkIds: string[]) {
    const covered = hkIds.filter(id => coverage[id] === 'primary').length;
    return `${covered} / ${hkIds.length}`;
  }

  async function handleToggle(hkId: string) {
    const key = `${bildungsplan}-${hkId}`;
    if (savingKey === key) return;
    const newVal = nextCoverage((coverage[hkId] as CoverageValue) ?? null);
    setSavingKey(key);
    try {
      await updateApHk(currentAP.code, bildungsplan, hkId, newVal ?? '');
    } finally {
      setSavingKey(null);
    }
  }

  return (
    <div className="page-body">
      <div className="ap-detail-head">
        <div className="ap-detail-left">
          <span className="ap-code-badge">{currentAP.code}</span>
          <span className="ap-detail-title">{pageTitle}</span>
        </div>
        <div className="ap-detail-summary">
          {summaryRows.map(row => (
            <div key={row.label} className="ap-summary-row">
              <span className="ap-summary-label">{row.label}</span>
              <span className="ap-summary-count">{calcSummary(row.hkIds)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="hk-legend">
        <span className="hk-icon hk-primary">●</span> Primär
        <span className="hk-icon hk-secondary" style={{ marginLeft: 16 }}>◐</span> Sekundär
        <span className="hk-icon hk-none" style={{ marginLeft: 16 }}>○</span> Nicht abgedeckt
        <span className="hk-legend-hint">Klick auf eine Zeile wechselt den Zustand und speichert automatisch.</span>
      </div>

      <div className="acc-list">
        {areas.map(area => (
          <AreaRow key={area.id}
            area={area}
            bildungsplan={bildungsplan}
            apCode={currentAP.code}
            coverage={coverage}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </div>
  );
}
