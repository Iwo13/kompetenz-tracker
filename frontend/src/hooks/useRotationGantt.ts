import { useState, useCallback } from 'react';

// ── Gantt-Koordinatensystem ────────────────────────────────────────────────────
// Monatsindex: Monate seit Januar 2024 (Index 0 = Jan 2024, 7 = Aug 2024, ...)
export const GANTT_START_YEAR = 2024;
export const GANTT_TOTAL_MO   = 84;   // 7 Jahre (2024–2030)
export const GANTT_ROW_H      = 44;
export const GANTT_SEC_H      = 28;

export const MONTHS_DE = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];

/** Datum → Monatsindex */
export function mo(year: number, month: number): number {
  return (year - GANTT_START_YEAR) * 12 + (month - 1);
}

/** ISO-Datum-String → Monatsindex */
export function dateToMo(d: string): number {
  const p = new Date(d);
  return mo(p.getFullYear(), p.getMonth() + 1);
}

/** Monatsindex → lesbarer String (z.B. "Aug 2024") */
export function moToLabel(m: number): string {
  const year  = GANTT_START_YEAR + Math.floor(m / 12);
  const month = ((m % 12) + 12) % 12;
  return `${MONTHS_DE[month]} ${year}`;
}

/** Heutiger Monatsindex */
export function getToday(): number {
  const n = new Date();
  return mo(n.getFullYear(), n.getMonth() + 1);
}

// ── AP-Farben (matching Mockup) ───────────────────────────────────────────────
export const AP_COLORS: Record<string, string> = {
  BLB:'#2563EB', BLM:'#1d4ed8', BLJ:'#2563EB', SDM:'#ea580c', SDO:'#f97316',
  SDW:'#fb923c', WE:'#0891b2',  COL:'#7c3aed',  EP:'#059669',  WEB:'#0284c7',
  SWE:'#1e3a5f', SA:'#be185d',  NetDC:'#dc2626', CIS:'#65a30d', PnD:'#9333ea',
  SBA:'#a16207', PnC:'#db2777',
};
const FALLBACK_COLORS = [
  '#0891b2','#7c3aed','#059669','#ea580c','#be185d',
  '#dc2626','#65a30d','#9333ea','#a16207','#0284c7',
];

export function getApColor(code: string, allCodes: string[]): string {
  if (AP_COLORS[code]) return AP_COLORS[code];
  const idx = allCodes.indexOf(code);
  return FALLBACK_COLORS[Math.max(0, idx) % FALLBACK_COLORS.length];
}

// ── Zoom-Hook ─────────────────────────────────────────────────────────────────
export type GanttZoom = 'sem' | 'mon';

export function useRotationGantt() {
  const [zoom, setZoomState] = useState<GanttZoom>('sem');

  const CW      = zoom === 'sem' ? 104 : 38;
  const numCols = zoom === 'sem' ? Math.ceil(GANTT_TOTAL_MO / 6) * 2 : GANTT_TOTAL_MO;

  const mToX = useCallback(
    (m: number) => zoom === 'sem' ? (m / 6) * 104 : m * 38,
    [zoom]
  );

  const dxToMo = useCallback(
    (dx: number) => zoom === 'sem' ? Math.round(dx / 104 * 6) : Math.round(dx / 38),
    [zoom]
  );

  /** Balken-Geometrie: v = erster Monat inkl., b = letzter Monat inkl. */
  const barGeom = useCallback(
    (v: number, b: number) => {
      const x = mToX(v);
      const w = Math.max(mToX(b + 1) - x, 18);
      return { x, w };
    },
    [mToX]
  );

  const setZoom = useCallback((z: GanttZoom) => setZoomState(z), []);

  return { zoom, setZoom, CW, numCols, mToX, dxToMo, barGeom };
}
