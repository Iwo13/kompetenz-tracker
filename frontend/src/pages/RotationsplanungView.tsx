import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import {
  getApColor, getToday, moToLabel, dateToMo, mo,
  GANTT_START_YEAR, GANTT_TOTAL_MO, GANTT_ROW_H, GANTT_SEC_H, MONTHS_DE,
} from '../hooks/useRotationGantt';
import type { User } from '../types';

// ── Typen ──────────────────────────────────────────────────────────────────────
interface GRot { id: string; userId: string; apCode: string; v: number; b: number; }
interface GRow { userId: string; name: string; lv: string; lv0: number; lv1: number; rots: GRot[]; }
interface GSec { label: string; rows: GRow[]; }
interface BarDrag {
  userId: string; rotId: string; apCode: string;
  mode: 'move' | 'left' | 'right';
  startX: number; origV: number; origB: number;
  barEl: HTMLDivElement;
  currentV?: number; currentB?: number;
}

const SPEC_LV: Record<string, string> = { app:'AE', platform:'PE', 'ict-fachmann':'FI' };
const LV_STYLE: Record<string, { bg: string; fg: string }> = {
  AE:{ bg:'#dbeafe', fg:'#1d4ed8' },
  PE:{ bg:'#dcfce7', fg:'#15803d' },
  FI:{ bg:'#fef3c7', fg:'#b45309' },
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function moToDateStr(m: number): string {
  const y  = GANTT_START_YEAR + Math.floor(m / 12);
  const mn = (m % 12) + 1;
  return `${y}-${String(mn).padStart(2, '0')}-01`;
}

function buildSections(users: User[]): GSec[] {
  const groups = new Map<string, { sy: number; ey: number; rows: GRow[] }>();
  for (const u of users) {
    if (!u.startDate) continue;
    const sd  = new Date(u.startDate);
    const sy  = sd.getFullYear();
    const dur = u.specialty === 'ict-fachmann' ? 3 : 4;
    const ey  = sy + dur;
    const key = `${sy}`;
    const lv0 = mo(sd.getFullYear(), sd.getMonth() + 1);
    const ed  = new Date(sd); ed.setFullYear(ed.getFullYear() + dur);
    const lv1 = mo(ed.getFullYear(), ed.getMonth() + 1);
    const rots: GRot[] = (u.rotations ?? []).map(r => ({
      id: r.id, userId: u.id, apCode: r.ap_code,
      v:  dateToMo(r.von),
      b:  r.bis ? dateToMo(r.bis) : Math.min(lv1, GANTT_TOTAL_MO - 1),
    }));
    if (!groups.has(key)) groups.set(key, { sy, ey, rows: [] });
    groups.get(key)!.rows.push({ userId: u.id, name: u.name, lv: SPEC_LV[u.specialty] ?? 'AE', lv0, lv1, rots });
  }
  return Array.from(groups.entries())
    .sort(([a],[b]) => a.localeCompare(b))
    .map(([,g]) => ({ label:`Jahrgang ${g.sy} – Abschluss ${g.ey}`, rows: g.rows.sort((a,b)=>a.name.localeCompare(b.name)) }));
}

function buildConflicts(secs: GSec[]): Record<string, Set<number>> {
  const cnt: Record<string, Record<number, number>> = {};
  for (const s of secs) for (const r of s.rows) for (const rot of r.rots)
    for (let m = rot.v; m <= rot.b; m++) {
      if (!cnt[rot.apCode]) cnt[rot.apCode] = {};
      cnt[rot.apCode][m] = (cnt[rot.apCode][m] ?? 0) + 1;
    }
  const cf: Record<string, Set<number>> = {};
  for (const [ap,ms] of Object.entries(cnt)) for (const [m,c] of Object.entries(ms))
    if (c > 1) (cf[ap] ??= new Set()).add(Number(m));
  return cf;
}

function rotConflict(rot: GRot, cf: Record<string, Set<number>>): boolean {
  const s = cf[rot.apCode]; if (!s) return false;
  for (let m = rot.v; m <= rot.b; m++) if (s.has(m)) return true;
  return false;
}

// ── Hauptkomponente ───────────────────────────────────────────────────────────
export default function RotationsplanungView() {
  const { users, ausbildungsplaetze, addRotation, updateRotation, deleteRotation } = useApp();
  const [zoom,        setZoom]        = useState<'sem'|'mon'>('sem');
  const [dragOverRow, setDragOverRow] = useState<string | null>(null);

  const chartRef = useRef<HTMLDivElement>(null);
  const namesRef = useRef<HTMLDivElement>(null);

  // Refs für Drag-Zustand (stabile Closure für Event-Listener)
  const barDragRef       = useRef<BarDrag | null>(null);
  const zoomRef          = useRef(zoom);
  const updateRotationRef = useRef(updateRotation);
  useEffect(() => { zoomRef.current = zoom; }, [zoom]);
  useEffect(() => { updateRotationRef.current = updateRotation; }, [updateRotation]);

  const TODAY   = useMemo(getToday, []);
  const sections  = useMemo(() => buildSections(users),    [users]);
  const conflicts = useMemo(() => buildConflicts(sections), [sections]);
  const apCodes   = useMemo(() => ausbildungsplaetze.map(a => a.code), [ausbildungsplaetze]);

  // Koordinaten-Hilfsfunktionen (lesen aus zoomRef für stabile Closures)
  function mXDirect(m: number): number {
    return zoomRef.current === 'sem' ? (m / 6) * 104 : m * 38;
  }

  // ── Bar-Drag Handlers (stabil via useCallback + leere Deps → nur Refs) ──────
  const handleBarMove = useCallback((e: MouseEvent) => {
    const d = barDragRef.current; if (!d) return;
    const isSeM = zoomRef.current === 'sem';
    const CW    = isSeM ? 104 : 38;
    const dmo   = isSeM ? Math.round((e.clientX - d.startX) / CW * 6) : Math.round((e.clientX - d.startX) / CW);
    const mX    = (m: number) => isSeM ? (m / 6) * CW : m * CW;
    const dur   = d.origB - d.origV;
    let v = d.origV, b = d.origB;
    if      (d.mode === 'move')  { v = Math.max(0, d.origV + dmo); b = v + dur; }
    else if (d.mode === 'left')  { v = Math.max(0, Math.min(d.origV + dmo, d.origB - 1)); }
    else                         { b = Math.max(d.origB + dmo, d.origV + 1); }
    d.currentV = v; d.currentB = b;
    const gx = mX(v), gw = Math.max(mX(b + 1) - gx, 18);
    d.barEl.style.left  = `${gx}px`;
    d.barEl.style.width = `${gw}px`;
  }, []);

  const handleBarUp = useCallback(async () => {
    document.removeEventListener('mousemove', handleBarMove);
    document.removeEventListener('mouseup',   handleBarUp);
    const d = barDragRef.current; if (!d) return;
    d.barEl.classList.remove('gantt-bar-dragging');
    barDragRef.current = null;
    const v = d.currentV ?? d.origV;
    const b = d.currentB ?? d.origB;
    if (v !== d.origV || b !== d.origB) {
      await updateRotationRef.current(d.userId, d.rotId, {
        ap_code: d.apCode, von: moToDateStr(v), bis: moToDateStr(b),
      }).catch(console.error);
    }
  }, [handleBarMove]);

  function startBarDrag(
    clientX: number, userId: string, rot: GRot,
    mode: 'move'|'left'|'right', barEl: HTMLDivElement
  ) {
    barDragRef.current = { userId, rotId: rot.id, apCode: rot.apCode, mode, startX: clientX, origV: rot.v, origB: rot.b, barEl };
    barEl.classList.add('gantt-bar-dragging');
    document.addEventListener('mousemove', handleBarMove);
    document.addEventListener('mouseup',   handleBarUp);
  }

  // ── Legend-Chip Drop auf Zeile ─────────────────────────────────────────────
  const handleLegendDrop = useCallback((e: React.DragEvent<HTMLDivElement>, row: GRow) => {
    e.preventDefault(); setDragOverRow(null);
    const apCode = e.dataTransfer.getData('ap'); if (!apCode) return;
    const cp = chartRef.current; if (!cp) return;
    const rect = cp.getBoundingClientRect();
    const xInChart = e.clientX - rect.left + cp.scrollLeft;
    const isSeM = zoomRef.current === 'sem';
    const CW  = isSeM ? 104 : 38;
    const dropMo = isSeM ? Math.floor(xInChart / CW * 6) : Math.floor(xInChart / CW);
    const v  = Math.max(0, Math.min(dropMo, GANTT_TOTAL_MO - 7));
    const b  = Math.min(v + 5, GANTT_TOTAL_MO - 1);
    addRotation(row.userId, { ap_code: apCode, von: moToDateStr(v), bis: moToDateStr(b) }).catch(console.error);
  }, [addRotation]);

  // ── Scroll-Sync ────────────────────────────────────────────────────────────
  useEffect(() => {
    const cp = chartRef.current, ns = namesRef.current;
    if (!cp || !ns) return;
    const sync = () => { ns.scrollTop = cp.scrollTop; };
    cp.addEventListener('scroll', sync, { passive: true });
    return () => cp.removeEventListener('scroll', sync);
  }, []);

  useEffect(() => {
    const cp = chartRef.current; if (!cp) return;
    cp.scrollLeft = Math.max(0, mXDirect(TODAY) - 200);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zoom]);

  // ── Gantt-Dimensionen ──────────────────────────────────────────────────────
  const CW      = zoom === 'sem' ? 104 : 38;
  const numCols = zoom === 'sem' ? 14 : GANTT_TOTAL_MO;
  const totalW  = numCols * CW;

  const flatRows = useMemo(() => {
    const out: Array<{type:'sec';label:string}|{type:'row';row:GRow}> = [];
    for (const s of sections) {
      out.push({ type:'sec', label:s.label });
      for (const r of s.rows) out.push({ type:'row', row:r });
    }
    return out;
  }, [sections]);

  const positions = useMemo(() => {
    let top = 0;
    return flatRows.map(item => { const y = top; top += item.type === 'sec' ? GANTT_SEC_H : GANTT_ROW_H; return y; });
  }, [flatRows]);

  const totalH = positions.length > 0
    ? positions[positions.length - 1] + (flatRows[flatRows.length - 1]?.type === 'sec' ? GANTT_SEC_H : GANTT_ROW_H)
    : 200;

  // ── Timeline-Header ────────────────────────────────────────────────────────
  const yearCells = useMemo(() => {
    const years: { year: number; cols: number }[] = [];
    for (let i = 0; i < numCols; i++) {
      const y = GANTT_START_YEAR + Math.floor(i / (zoom === 'sem' ? 2 : 12));
      if (!years.length || years[years.length-1].year !== y) years.push({ year:y, cols:1 });
      else years[years.length-1].cols++;
    }
    return years;
  }, [zoom, numCols]);

  const colLabels = useMemo(() => Array.from({ length:numCols }, (_,i) => {
    if (zoom === 'sem') { const y = String(GANTT_START_YEAR + Math.floor(i/2)).slice(2); return i%2===0 ? `${y}Fr` : `${y}He`; }
    return MONTHS_DE[i % 12];
  }), [zoom, numCols]);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="gantt-page">

      {/* ── Header ── */}
      <div className="gantt-header">
        <span className="gantt-title">Rotationsplanung</span>
        <button className="gantt-btn gantt-btn-today"
          onClick={() => { if(chartRef.current) chartRef.current.scrollLeft = Math.max(0, mXDirect(TODAY) - 200); }}>
          ▶ Heute
        </button>
        <div className="gantt-zoom-group">
          <button className={`gantt-btn${zoom==='sem'?' gantt-btn-active':''}`} onClick={() => setZoom('sem')}>Semester</button>
          <button className={`gantt-btn${zoom==='mon'?' gantt-btn-active':''}`} onClick={() => setZoom('mon')}>Monat</button>
        </div>
<div className="gantt-conflict-hint">
          <div className="gantt-conflict-dot" />
          <span>= AP-Konflikt</span>
        </div>
      </div>

      {/* ── Legende (alle verfügbaren APs, drag-fähig) ── */}
      <div className="gantt-legend">
        {ausbildungsplaetze.map(ap => {
          const color = getApColor(ap.code, apCodes);
          return (
            <div key={ap.code} className="gantt-lchip"
              draggable
              onDragStart={e => { e.dataTransfer.setData('ap', ap.code); e.dataTransfer.effectAllowed = 'copy'; }}
              title={`${ap.name} – auf eine Zeile ziehen zum Zuweisen`}
              style={{ cursor:'grab' }}
            >
              <div className="gantt-ldot" style={{ background:color }} />
              <span>{ap.code} – {ap.name}</span>
            </div>
          );
        })}
      </div>

      {/* ── Gantt-Body ── */}
      <div className="gantt-body">

        {/* Namen-Panel */}
        <div className="gantt-names-panel">
          <div className="gantt-names-head">Lernende</div>
          <div className="gantt-names-scroll" ref={namesRef}>
            <div style={{ position:'relative', height:totalH }}>
              {flatRows.map((item, i) => (
                item.type === 'sec' ? (
                  <div key={i} className="gantt-sec-label"
                    style={{ position:'absolute', top:positions[i], left:0, right:0, height:GANTT_SEC_H }}>
                    {item.label}
                  </div>
                ) : (
                  <div key={i} className="gantt-name-row"
                    style={{ position:'absolute', top:positions[i], left:0, right:0, height:GANTT_ROW_H }}>
                    <span className="gantt-rname">{item.row.name}</span>
                    {(() => {
                      const st = LV_STYLE[item.row.lv] ?? { bg:'#f1f5f9', fg:'#475569' };
                      return <span className="gantt-lv" style={{ background:st.bg, color:st.fg }}>{item.row.lv}</span>;
                    })()}
                  </div>
                )
              ))}
            </div>
          </div>
        </div>

        {/* Chart-Panel */}
        <div className="gantt-chart-panel" ref={chartRef}>
          <div style={{ position:'relative', width:totalW, minHeight:'100%' }}>

            {/* Timeline-Header (sticky) */}
            <div className="gantt-tlhead" style={{ width:totalW }}>
              <div className="gantt-year-row">
                {yearCells.map((yc,i) => (
                  <div key={i} className="gantt-ycell" style={{ width:yc.cols*CW }}>{yc.year}</div>
                ))}
              </div>
              <div className="gantt-col-row">
                {colLabels.map((lbl,i) => {
                  const grp = zoom === 'sem' ? i : Math.floor(i/6);
                  return (
                    <div key={i} className={`gantt-ccell ${grp%2===0?'gantt-odd':'gantt-even'}`}
                      style={{ width:CW, fontSize:zoom==='mon'?9:undefined }}>
                      {lbl}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Inhalt */}
            <div className="gantt-cc" style={{ width:totalW, height:totalH }}>

              {/* Gitterlinien */}
              {Array.from({ length:numCols+1 }, (_,i) => {
                const isBig = zoom==='sem' ? i%2===0 : i%12===0;
                const isMid = zoom!=='sem' && i%6===0;
                return (
                  <div key={i} className="gantt-gl" style={{
                    left: i*CW,
                    width: isBig?2:isMid?1.5:1,
                    background: isBig?'#d1d5db':isMid?'#e5e7eb':'#f5f5f5',
                  }} />
                );
              })}

              {/* Heute-Linie */}
              <div className="gantt-today-line" style={{ left:mXDirect(TODAY) }}>
                <div className="gantt-today-lbl">Heute</div>
              </div>

              {/* Zeilen */}
              {flatRows.map((item,i) => {
                if (item.type === 'sec') {
                  return <div key={i} className="gantt-sec-r"
                    style={{ top:positions[i], width:totalW, height:GANTT_SEC_H }} />;
                }

                const row = item.row;
                const lbX = mXDirect(Math.max(row.lv0, 0));
                const lbW = Math.max(mXDirect(Math.min(row.lv1, GANTT_TOTAL_MO-1)+1) - lbX, 0);

                return (
                  <div key={i}
                    className={`gantt-drow${dragOverRow===row.userId?' gantt-drop-target':''}`}
                    style={{ top:positions[i], height:GANTT_ROW_H, width:totalW }}
                    onDragOver={e => { e.preventDefault(); e.dataTransfer.dropEffect='copy'; setDragOverRow(row.userId); }}
                    onDragLeave={() => setDragOverRow(null)}
                    onDrop={e => handleLegendDrop(e, row)}
                  >
                    {/* Lehrzeit-Hintergrund */}
                    {lbW > 0 && (
                      <div className="gantt-lehr-bg" style={{ left:lbX, width:lbW, background:'rgba(219,234,254,.4)' }} />
                    )}

                    {/* "noch X Mt." */}
                    {row.lv1 > TODAY && row.lv1 < GANTT_TOTAL_MO && (
                      <div className="gantt-rem" style={{ left:mXDirect(row.lv1+1)+3 }}>
                        noch {row.lv1 - TODAY} Mt.
                      </div>
                    )}

                    {/* Rotations-Balken */}
                    {row.rots.map(rot => {
                      const gx      = mXDirect(rot.v);
                      const gw      = Math.max(mXDirect(rot.b+1) - gx, 18);
                      const color   = getApColor(rot.apCode, apCodes);
                      const conflict = rotConflict(rot, conflicts);
                      return (
                        <div
                          key={rot.id}
                          className={`gantt-bar${conflict?' gantt-conflict':''}`}
                          style={{ left:gx, width:gw, background:color, cursor:'grab' }}
                          title={`${rot.apCode} – ${moToLabel(rot.v)} bis ${moToLabel(rot.b)}`}
                          onMouseDown={e => {
                            const t = e.target as HTMLElement;
                            if (t.closest('.gantt-hdl') || t.classList.contains('gantt-del-btn')) return;
                            startBarDrag(e.clientX, row.userId, rot, 'move', e.currentTarget as HTMLDivElement);
                          }}
                        >
                          {/* Linker Resize-Griff */}
                          <div className="gantt-hdl gantt-hdl-l"
                            onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, row.userId, rot, 'left', e.currentTarget.parentElement as HTMLDivElement); }} />

                          <span className="gantt-bar-lbl">{rot.apCode}</span>

                          {/* Rechter Resize-Griff */}
                          <div className="gantt-hdl gantt-hdl-r"
                            onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, row.userId, rot, 'right', e.currentTarget.parentElement as HTMLDivElement); }} />

                          <button className="gantt-del-btn"
                            onClick={e => { e.stopPropagation(); if(window.confirm('Einsatz entfernen?')) deleteRotation(row.userId, rot.id).catch(console.error); }}
                            title="Entfernen">×</button>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
