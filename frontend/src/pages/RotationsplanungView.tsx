import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import {
  getApColor, getToday, moToLabel, dateToMo, mo,
  GANTT_START_YEAR, GANTT_TOTAL_MO, GANTT_ROW_H, GANTT_SEC_H, MONTHS_DE,
} from '../hooks/useRotationGantt';
import APModal from '../components/APModal';
import type { User, Ausbildungsplatz } from '../types';

// ── Typen ──────────────────────────────────────────────────────────────────────
interface GRot    { id: string; userId: string; apCode: string; v: number; b: number; }
interface GRow    { userId: string; name: string; lv: string; lv0: number; lv1: number; rots: GRot[]; }
interface GSec    { label: string; rows: GRow[]; }
interface APGRot  { id: string; userId: string; userName: string; lv: string; v: number; b: number; lv0: number; lv1: number; }
interface APGRow  { ap: Ausbildungsplatz; fokus: string; rots: APGRot[]; }

interface BarDrag {
  userId: string; rotId: string; apCode: string;
  mode: 'move' | 'left' | 'right';
  startX: number; origV: number; origB: number;
  barEl: HTMLDivElement;
  currentV?: number; currentB?: number;
  lv0: number; lv1: number;
}

const SPEC_LV: Record<string, string> = { app:'AE', platform:'PE', 'ict-fachmann':'FI' };
const LV_STYLE: Record<string, { bg: string; fg: string }> = {
  AE:{ bg:'#dbeafe', fg:'#1d4ed8' },
  PE:{ bg:'#dcfce7', fg:'#15803d' },
  FI:{ bg:'#fef3c7', fg:'#b45309' },
};

// Farben für Lernenden-Balken in der AP-Sicht
const USER_COLORS = [
  '#2563EB','#059669','#d97706','#7c3aed','#db2777',
  '#0891b2','#dc2626','#65a30d','#9333ea','#ea580c',
  '#be185d','#0284c7','#a16207','#1e3a5f','#6d28d9',
];
function getUserColor(userId: string, allIds: string[]): string {
  const idx = allIds.indexOf(userId);
  return USER_COLORS[Math.max(0, idx) % USER_COLORS.length];
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function moToDateStr(m: number): string {
  const y  = GANTT_START_YEAR + Math.floor(m / 12);
  const mn = (m % 12) + 1;
  return `${y}-${String(mn).padStart(2, '0')}-01`;
}

function userLv(u: User): { lv0: number; lv1: number } {
  const sd  = new Date(u.startDate ?? u.start_date);
  const dur = u.specialty === 'ict-fachmann' ? 3 : 4;
  const lv0 = mo(sd.getFullYear(), sd.getMonth() + 1);
  const ed  = new Date(sd); ed.setFullYear(sd.getFullYear() + dur);
  return { lv0, lv1: mo(ed.getFullYear(), ed.getMonth() + 1) };
}

function buildSections(users: User[]): GSec[] {
  const groups = new Map<string, { sy: number; ey: number; rows: GRow[] }>();
  for (const u of users) {
    if (!u.startDate) continue;
    const sd  = new Date(u.startDate);
    const sy  = sd.getFullYear();
    const dur = u.specialty === 'ict-fachmann' ? 3 : 4;
    const ey  = sy + dur;
    const { lv0, lv1 } = userLv(u);
    const rots: GRot[] = (u.rotations ?? []).map(r => ({
      id: r.id, userId: u.id, apCode: r.ap_code,
      v:  dateToMo(r.von),
      b:  Math.min(r.bis ? dateToMo(r.bis) : lv1, lv1, GANTT_TOTAL_MO - 1),
    }));
    if (!groups.has(String(sy))) groups.set(String(sy), { sy, ey, rows: [] });
    groups.get(String(sy))!.rows.push({ userId: u.id, name: u.name, lv: SPEC_LV[u.specialty] ?? 'AE', lv0, lv1, rots });
  }
  return Array.from(groups.entries())
    .sort(([a],[b]) => a.localeCompare(b))
    .map(([,g]) => ({ label:`Jahrgang ${g.sy} – Abschluss ${g.ey}`, rows: g.rows.sort((a,b)=>a.name.localeCompare(b.name)) }));
}

function buildAPRows(aps: Ausbildungsplatz[], users: User[]): APGRow[] {
  return aps.map(ap => {
    const rots: APGRot[] = [];
    for (const u of users) {
      if (!u.startDate) continue;
      const { lv0, lv1 } = userLv(u);
      for (const r of u.rotations ?? []) {
        if (r.ap_code !== ap.code) continue;
        rots.push({
          id: r.id, userId: u.id, userName: u.name,
          lv: SPEC_LV[u.specialty] ?? 'AE',
          v:  dateToMo(r.von),
          b:  Math.min(r.bis ? dateToMo(r.bis) : lv1, lv1, GANTT_TOTAL_MO - 1),
          lv0, lv1,
        });
      }
    }
    const lvSet = new Set(rots.map(r => r.lv));
    const fokus = lvSet.size === 0 ? '–' : [...lvSet].sort().join('/');
    return { ap, fokus, rots };
  });
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
  const { users, ausbildungsplaetze, addRotation, updateRotation, deleteRotation,
          rotationGanttView: view, setRotationGanttView: setView } = useApp();
  const [zoom,          setZoom]          = useState<'sem'|'mon'>('sem');
  const [dragOverRow,   setDragOverRow]   = useState<string | null>(null);
  const [dragOverAPRow, setDragOverAPRow] = useState<string | null>(null);
  const [showAddAP,     setShowAddAP]     = useState(false);

  const chartRef  = useRef<HTMLDivElement>(null);
  const namesRef  = useRef<HTMLDivElement>(null);
  const barDragRef        = useRef<BarDrag | null>(null);
  const zoomRef           = useRef(zoom);
  const updateRotationRef = useRef(updateRotation);
  useEffect(() => { zoomRef.current = zoom; },             [zoom]);
  useEffect(() => { updateRotationRef.current = updateRotation; }, [updateRotation]);

  const TODAY     = useMemo(getToday, []);
  const sections  = useMemo(() => buildSections(users),           [users]);
  const apRows    = useMemo(() => buildAPRows(ausbildungsplaetze, users), [ausbildungsplaetze, users]);
  const conflicts = useMemo(() => buildConflicts(sections),        [sections]);
  const apCodes   = useMemo(() => ausbildungsplaetze.map(a => a.code), [ausbildungsplaetze]);
  const userIds   = useMemo(() => users.map(u => u.id),            [users]);

  function mXDirect(m: number): number {
    return zoomRef.current === 'sem' ? (m / 6) * 104 : m * 38;
  }

  // ── Bar-Drag Handlers ──────────────────────────────────────────────────────
  const handleBarMove = useCallback((e: MouseEvent) => {
    const d = barDragRef.current; if (!d) return;
    const isSeM = zoomRef.current === 'sem';
    const CW    = isSeM ? 104 : 38;
    const dmo   = isSeM ? Math.round((e.clientX - d.startX) / CW * 6) : Math.round((e.clientX - d.startX) / CW);
    const mX    = (m: number) => isSeM ? (m / 6) * CW : m * CW;
    const dur        = d.origB - d.origV;
    const { lv0, lv1 } = d;
    let v = d.origV, b = d.origB;
    if (d.mode === 'move') {
      v = Math.max(lv0, d.origV + dmo);
      b = v + dur;
      if (b > lv1) { b = lv1; v = Math.max(lv0, b - dur); }
    } else if (d.mode === 'left') {
      v = Math.max(lv0, Math.min(d.origV + dmo, d.origB - 1));
    } else {
      b = Math.min(Math.max(d.origB + dmo, d.origV + 1), lv1);
    }
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
    mode: 'move'|'left'|'right', barEl: HTMLDivElement,
    lv0: number, lv1: number
  ) {
    barDragRef.current = { userId, rotId: rot.id, apCode: rot.apCode, mode, startX: clientX, origV: rot.v, origB: rot.b, barEl, lv0, lv1 };
    barEl.classList.add('gantt-bar-dragging');
    document.addEventListener('mousemove', handleBarMove);
    document.addEventListener('mouseup',   handleBarUp);
  }

  // ── Legend-Drop: AP-Chip auf Lernenden-Zeile ──────────────────────────────
  const handleLegendDrop = useCallback((e: React.DragEvent<HTMLDivElement>, row: GRow) => {
    e.preventDefault(); setDragOverRow(null);
    const apCode = e.dataTransfer.getData('ap'); if (!apCode) return;
    const cp = chartRef.current; if (!cp) return;
    const rect = cp.getBoundingClientRect();
    const xInChart = e.clientX - rect.left + cp.scrollLeft;
    const isSeM = zoomRef.current === 'sem';
    const CW    = isSeM ? 104 : 38;
    const dropMo = isSeM ? Math.floor(xInChart / CW * 6) : Math.floor(xInChart / CW);
    if (dropMo > row.lv1) return;
    const v = Math.max(row.lv0, Math.min(dropMo, row.lv1));
    const b = Math.min(v + 5, row.lv1);
    addRotation(row.userId, { ap_code: apCode, von: moToDateStr(v), bis: moToDateStr(b) }).catch(console.error);
  }, [addRotation]);

  // ── Legend-Drop: Lernenden-Chip auf AP-Zeile ──────────────────────────────
  const handleLearnerDrop = useCallback((e: React.DragEvent<HTMLDivElement>, apCode: string) => {
    e.preventDefault(); setDragOverAPRow(null);
    const userId = e.dataTransfer.getData('userId'); if (!userId) return;
    const user = users.find(u => u.id === userId); if (!user || !user.startDate) return;
    const cp = chartRef.current; if (!cp) return;
    const rect = cp.getBoundingClientRect();
    const xInChart = e.clientX - rect.left + cp.scrollLeft;
    const isSeM = zoomRef.current === 'sem';
    const CW    = isSeM ? 104 : 38;
    const dropMo = isSeM ? Math.floor(xInChart / CW * 6) : Math.floor(xInChart / CW);
    const { lv0, lv1 } = userLv(user);
    if (dropMo > lv1 || dropMo < lv0) return;
    const v = Math.max(lv0, Math.min(dropMo, lv1));
    const b = Math.min(v + 5, lv1);
    addRotation(userId, { ap_code: apCode, von: moToDateStr(v), bis: moToDateStr(b) }).catch(console.error);
  }, [users, addRotation]);

  // ── Scroll-Sync (neu nach View-Wechsel) ───────────────────────────────────
  useEffect(() => {
    const cp = chartRef.current, ns = namesRef.current;
    if (!cp || !ns) return;
    const sync = () => { ns.scrollTop = cp.scrollTop; };
    cp.addEventListener('scroll', sync, { passive: true });
    return () => cp.removeEventListener('scroll', sync);
  }, [view]);

  // ── Scroll zu Heute (bei Zoom- oder View-Wechsel) ─────────────────────────
  useEffect(() => {
    const cp = chartRef.current; if (!cp) return;
    const isSeM = zoomRef.current === 'sem';
    const CW = isSeM ? 104 : 38;
    const x  = isSeM ? (TODAY / 6) * CW : TODAY * CW;
    cp.scrollLeft = Math.max(0, x - 200);
  }, [zoom, view, TODAY]);

  // ── Gantt-Dimensionen ──────────────────────────────────────────────────────
  const CW      = zoom === 'sem' ? 104 : 38;
  const numCols = zoom === 'sem' ? 14 : GANTT_TOTAL_MO;
  const totalW  = numCols * CW;

  // Lernende-Sicht: flache Zeilen mit Sektionen
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

  // AP-Sicht: flache Zeilen (eine pro AP)
  const apTotalH = apRows.length * GANTT_ROW_H || 200;

  // ── Timeline-Header (gemeinsam) ────────────────────────────────────────────
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

  // ── Timeline Header JSX (geteilt zwischen beiden Sichten) ─────────────────
  const timelineHeader = (
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
  );

  // ── Grid-Linien JSX (geteilt) ──────────────────────────────────────────────
  const gridLines = Array.from({ length:numCols+1 }, (_,i) => {
    const isBig = zoom==='sem' ? i%2===0 : i%12===0;
    const isMid = zoom!=='sem' && i%6===0;
    return (
      <div key={i} className="gantt-gl" style={{
        left: i*CW,
        width: isBig?2:isMid?1.5:1,
        background: isBig?'#d1d5db':isMid?'#e5e7eb':'#f5f5f5',
      }} />
    );
  });

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="gantt-page">

      {/* ── Header ── */}
      <div className="gantt-header">
        <span className="gantt-title">Rotationsplanung</span>
        <button className="gantt-btn gantt-btn-today" onClick={() => {
          const cp = chartRef.current; if (!cp) return;
          const isSeM = zoomRef.current === 'sem';
          const CW = isSeM ? 104 : 38;
          cp.scrollLeft = Math.max(0, (isSeM ? (TODAY / 6) * CW : TODAY * CW) - 200);
        }}>▶ Heute</button>

        {/* Sicht-Toggle */}
        <div className="gantt-zoom-group">
          <button className={`gantt-btn${view==='lernende'?' gantt-btn-active':''}`}
            onClick={() => setView('lernende')}>Lernende</button>
          <button className={`gantt-btn${view==='ausbildungsplaetze'?' gantt-btn-active':''}`}
            onClick={() => setView('ausbildungsplaetze')}>Ausbildungsplätze</button>
        </div>

        <div className="gantt-zoom-group">
          <button className={`gantt-btn${zoom==='sem'?' gantt-btn-active':''}`} onClick={() => setZoom('sem')}>Semester</button>
          <button className={`gantt-btn${zoom==='mon'?' gantt-btn-active':''}`} onClick={() => setZoom('mon')}>Monat</button>
        </div>

        {view === 'lernende' && (
          <div className="gantt-conflict-hint">
            <div className="gantt-conflict-dot" />
            <span>= AP-Konflikt</span>
          </div>
        )}
      </div>

      {/* ── Legende ── */}
      <div className="gantt-legend">
        {view === 'lernende' ? (
          // Lernende-Sicht: AP-Chips als Drag-Quelle
          ausbildungsplaetze.map(ap => {
            const color = getApColor(ap.code, apCodes);
            return (
              <div key={ap.code} className="gantt-lchip"
                draggable
                onDragStart={e => { e.dataTransfer.setData('ap', ap.code); e.dataTransfer.effectAllowed = 'copy'; }}
                title={`${ap.name} – auf eine Zeile ziehen`}
                style={{ cursor:'grab' }}
              >
                <div className="gantt-ldot" style={{ background:color }} />
                <span>{ap.code} – {ap.name}</span>
              </div>
            );
          })
        ) : (
          // AP-Sicht: Lernenden-Chips als Drag-Quelle + Neuer AP Button
          <>
            {users.map(u => {
              const lv = SPEC_LV[u.specialty] ?? 'AE';
              const st = LV_STYLE[lv] ?? { bg:'#f1f5f9', fg:'#475569' };
              const color = getUserColor(u.id, userIds);
              return (
                <div key={u.id} className="gantt-lchip"
                  draggable
                  onDragStart={e => { e.dataTransfer.setData('userId', u.id); e.dataTransfer.effectAllowed = 'copy'; }}
                  title={`${u.name} – auf AP-Zeile ziehen`}
                  style={{ cursor:'grab' }}
                >
                  <div className="gantt-ldot" style={{ background:color }} />
                  <span>{u.name}</span>
                  <span style={{ marginLeft:5, fontSize:'0.7rem', background:st.bg, color:st.fg, padding:'1px 5px', fontWeight:700 }}>{lv}</span>
                </div>
              );
            })}
            <button
              className="gantt-btn"
              style={{ marginLeft:'auto', fontWeight:700, background:'var(--fhnw-yellow)', borderColor:'var(--fhnw-yellow-hover)' }}
              onClick={() => setShowAddAP(true)}
            >+ Neuer AP</button>
          </>
        )}
      </div>

      {/* ── Gantt-Body ── */}
      <div className="gantt-body">

        {/* ── LERNENDE-SICHT ── */}
        {view === 'lernende' && (<>
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

          {/* Chart-Panel Lernende */}
          <div className="gantt-chart-panel" ref={chartRef}>
            <div style={{ position:'relative', width:totalW, minHeight:'100%' }}>
              {timelineHeader}
              <div className="gantt-cc" style={{ width:totalW, height:totalH }}>
                {gridLines}
                <div className="gantt-today-line" style={{ left:mXDirect(TODAY) }}>
                  <div className="gantt-today-lbl">Heute</div>
                </div>
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
                      {lbW > 0 && (
                        <div className="gantt-lehr-bg" style={{ left:lbX, width:lbW, background:'rgba(219,234,254,.4)' }} />
                      )}
                      {row.lv1 > TODAY && row.lv1 < GANTT_TOTAL_MO && (
                        <div className="gantt-rem" style={{ left:mXDirect(row.lv1+1)+3 }}>
                          noch {row.lv1 - TODAY} Mt.
                        </div>
                      )}
                      {row.rots.map(rot => {
                        const gx      = mXDirect(rot.v);
                        const gw      = Math.max(mXDirect(rot.b+1) - gx, 18);
                        const color   = getApColor(rot.apCode, apCodes);
                        const conflict = rotConflict(rot, conflicts);
                        return (
                          <div key={rot.id}
                            className={`gantt-bar${conflict?' gantt-conflict':''}`}
                            style={{ left:gx, width:gw, background:color, cursor:'grab' }}
                            title={`${rot.apCode} – ${moToLabel(rot.v)} bis ${moToLabel(rot.b)}`}
                            onMouseDown={e => {
                              const t = e.target as HTMLElement;
                              if (t.closest('.gantt-hdl') || t.classList.contains('gantt-del-btn')) return;
                              startBarDrag(e.clientX, row.userId, rot, 'move', e.currentTarget as HTMLDivElement, row.lv0, row.lv1);
                            }}
                          >
                            <div className="gantt-hdl gantt-hdl-l"
                              onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, row.userId, rot, 'left', e.currentTarget.parentElement as HTMLDivElement, row.lv0, row.lv1); }} />
                            <span className="gantt-bar-lbl">{rot.apCode}</span>
                            <div className="gantt-hdl gantt-hdl-r"
                              onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, row.userId, rot, 'right', e.currentTarget.parentElement as HTMLDivElement, row.lv0, row.lv1); }} />
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
        </>)}

        {/* ── AUSBILDUNGSPLÄTZE-SICHT ── */}
        {view === 'ausbildungsplaetze' && (<>
          {/* Namen-Panel */}
          <div className="gantt-names-panel">
            <div className="gantt-names-head">Ausbildungsplätze</div>
            <div className="gantt-names-scroll" ref={namesRef}>
              <div style={{ position:'relative', height:apTotalH }}>
                {apRows.map((apRow, i) => {
                  const lvs   = apRow.fokus.split('/').filter(s => s !== '–');
                  const st    = lvs.length === 1 ? (LV_STYLE[lvs[0]] ?? { bg:'#f1f5f9', fg:'#475569' }) : { bg:'#f1f5f9', fg:'#475569' };
                  return (
                    <div key={apRow.ap.code} className="gantt-name-row"
                      style={{ position:'absolute', top:i*GANTT_ROW_H, left:0, right:0, height:GANTT_ROW_H }}>
                      <span className="gantt-rname" style={{ fontSize:'0.75rem' }}>
                        <strong>{apRow.ap.code}</strong> {apRow.ap.name}
                      </span>
                      {apRow.fokus !== '–' && (
                        <span className="gantt-lv" style={{ background:st.bg, color:st.fg, fontSize:'0.6rem' }}>
                          {apRow.fokus}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Chart-Panel Ausbildungsplätze */}
          <div className="gantt-chart-panel" ref={chartRef}>
            <div style={{ position:'relative', width:totalW, minHeight:'100%' }}>
              {timelineHeader}
              <div className="gantt-cc" style={{ width:totalW, height:apTotalH }}>
                {gridLines}
                <div className="gantt-today-line" style={{ left:mXDirect(TODAY) }}>
                  <div className="gantt-today-lbl">Heute</div>
                </div>
                {apRows.map((apRow, i) => (
                  <div key={apRow.ap.code}
                    className={`gantt-drow${dragOverAPRow===apRow.ap.code?' gantt-drop-target':''}`}
                    style={{ top:i*GANTT_ROW_H, height:GANTT_ROW_H, width:totalW }}
                    onDragOver={e => { e.preventDefault(); e.dataTransfer.dropEffect='copy'; setDragOverAPRow(apRow.ap.code); }}
                    onDragLeave={() => setDragOverAPRow(null)}
                    onDrop={e => handleLearnerDrop(e, apRow.ap.code)}
                  >
                    {apRow.rots.map(rot => {
                      const gx    = mXDirect(rot.v);
                      const gw    = Math.max(mXDirect(rot.b+1) - gx, 18);
                      const color = getUserColor(rot.userId, userIds);
                      const gRot: GRot = { id:rot.id, userId:rot.userId, apCode:apRow.ap.code, v:rot.v, b:rot.b };
                      const shortName = `${rot.userName.split(' ')[0]} (${rot.lv})`;
                      return (
                        <div key={rot.id}
                          className="gantt-bar"
                          style={{ left:gx, width:gw, background:color, cursor:'grab' }}
                          title={`${rot.userName} – ${moToLabel(rot.v)} bis ${moToLabel(rot.b)}`}
                          onMouseDown={e => {
                            const t = e.target as HTMLElement;
                            if (t.closest('.gantt-hdl') || t.classList.contains('gantt-del-btn')) return;
                            startBarDrag(e.clientX, rot.userId, gRot, 'move', e.currentTarget as HTMLDivElement, rot.lv0, rot.lv1);
                          }}
                        >
                          <div className="gantt-hdl gantt-hdl-l"
                            onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, rot.userId, gRot, 'left', e.currentTarget.parentElement as HTMLDivElement, rot.lv0, rot.lv1); }} />
                          <span className="gantt-bar-lbl">{shortName}</span>
                          <div className="gantt-hdl gantt-hdl-r"
                            onMouseDown={e => { e.stopPropagation(); startBarDrag(e.clientX, rot.userId, gRot, 'right', e.currentTarget.parentElement as HTMLDivElement, rot.lv0, rot.lv1); }} />
                          <button className="gantt-del-btn"
                            onClick={e => { e.stopPropagation(); if(window.confirm('Einsatz entfernen?')) deleteRotation(rot.userId, rot.id).catch(console.error); }}
                            title="Entfernen">×</button>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>)}

      </div>
      {showAddAP && <APModal onClose={() => setShowAddAP(false)} />}
    </div>
  );
}
