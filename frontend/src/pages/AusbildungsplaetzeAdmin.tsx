import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import type { Area, Ausbildungsplatz } from '../types';

const AREA_CODES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

type CoverageVal = 'primary' | 'secondary' | null | undefined;

function nextCoverage(val: CoverageVal): string | null {
  if (!val)              return 'secondary';
  if (val === 'secondary') return 'primary';
  return null;
}

function getPlacement(code: string): string {
  const idx = AREA_CODES.indexOf(code);
  if (idx <= 1) return 'bottom-start';
  if (idx >= 6) return 'bottom-end';
  return 'bottom';
}

function AreaHeaderCell({ area }: { area: Area }) {
  const [visible, setVisible] = useState(false);
  const placement = getPlacement(area.id);

  return (
    <th
      className={`ap-th-area${visible ? ' ap-th-hover' : ''}`}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      <div className="ap-area-header-inner">
        <span className="ap-area-letter">{area.id.toUpperCase()}</span>
        <span className="ap-area-th-name">{area.name}</span>
      </div>

      {visible && (
        <div className={`bs-popover bs-popover-${placement}`} role="tooltip">
          <div className="popover-arrow" />
          <div className="popover-header">{area.id.toUpperCase()}: {area.name}</div>
          <div className="popover-body">
            <ul className="popover-goals-list">
              {area.subComps.map(sc => (
                <li key={sc.id}>
                  <span className="popover-sc-id">{sc.id}</span> {sc.name}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </th>
  );
}

interface CoverageCellProps {
  value:   CoverageVal;
  saving:  boolean;
  onClick: () => void;
}
function CoverageCell({ value, saving, onClick }: CoverageCellProps) {
  const label = value === 'primary' ? '●' : value === 'secondary' ? '◐' : '○';
  const title = value === 'primary' ? 'Primär'
              : value === 'secondary' ? 'Sekundär'
              : 'Nicht zugeordnet';
  return (
    <button
      className={`ap-cell ap-cell-${value ?? 'none'}${saving ? ' ap-cell-saving' : ''}`}
      onClick={onClick}
      title={title}
      disabled={saving}
    >
      {saving ? '…' : label}
    </button>
  );
}

export default function AusbildungsplaetzeAdmin() {
  const { areasInformatiker } = useApp();
  const [aps,     setAps]     = useState<Ausbildungsplatz[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingCell, setSaving] = useState<string | null>(null);

  useEffect(() => {
    api.getAusbildungsplaetze()
      .then(data => setAps(data.ausbildungsplaetze))
      .finally(() => setLoading(false));
  }, []);

  const areaMap: Record<string, Area> = Object.fromEntries(
    (areasInformatiker ?? []).map(a => [a.id, a])
  );

  async function toggleCell(ap: Ausbildungsplatz, areaCode: string) {
    const key    = `${ap.code}-${areaCode}`;
    const newVal = nextCoverage((ap.bereiche?.[areaCode] as CoverageVal) ?? null);
    const newBereiche = { ...ap.bereiche, [areaCode]: newVal };

    setAps(prev => prev.map(a =>
      a.code === ap.code ? { ...a, bereiche: newBereiche as Ausbildungsplatz['bereiche'] } : a
    ));
    setSaving(key);
    try {
      await api.updateApBereiche(ap.code, Object.values(newBereiche).filter(Boolean) as string[]);
    } catch {
      setAps(prev => prev.map(a => a.code === ap.code ? { ...a, bereiche: ap.bereiche } : a));
    } finally {
      setSaving(null);
    }
  }

  if (loading) return <div className="page-body"><p>Lade Ausbildungsplätze…</p></div>;

  return (
    <div className="page-body">
      <div className="ap-admin-header">
        <h2>Ausbildungsplätze verwalten</h2>
        <p className="ap-admin-sub">
          Klick auf eine Zelle speichert automatisch. Hover über Bereichs-Kopf für Handlungskompetenzen.
          <span className="ap-legend-item ap-cell-none">○ Nicht zugeordnet</span>
          <span className="ap-legend-item ap-cell-secondary">◐ Sekundär</span>
          <span className="ap-legend-item ap-cell-primary">● Primär</span>
        </p>
      </div>

      <div className="ap-matrix-wrap">
        <table className="ap-matrix">
          <thead>
            <tr>
              <th className="ap-th-ap">Ausbildungsplatz</th>
              {AREA_CODES.map(a =>
                areaMap[a]
                  ? <AreaHeaderCell key={a} area={areaMap[a]} />
                  : <th key={a} className="ap-th-area">{a.toUpperCase()}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {aps.map(ap => (
              <tr key={ap.code} className="ap-row">
                <td className="ap-name-cell">
                  <div className="ap-code">{ap.code}</div>
                  <div className="ap-fullname">{ap.name}</div>
                  <div className="ap-lj">ab {ap.abLehrjahr}. LJ</div>
                </td>
                {AREA_CODES.map(a => (
                  <td key={a} className="ap-cell-wrap">
                    <CoverageCell
                      value={ap.bereiche?.[a] as CoverageVal}
                      saving={savingCell === `${ap.code}-${a}`}
                      onClick={() => toggleCell(ap, a)}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
