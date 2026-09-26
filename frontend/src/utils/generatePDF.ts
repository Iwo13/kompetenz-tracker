import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { SPECIALTY_LABEL, getLehrjahrInfo, getAreaProgress, getOverallProgress } from '../utils';
import type { User, Area, UserDocument } from '../types';

export type RGB = [number, number, number];

export const FHNW_YELLOW: RGB = [253, 231, 14];
export const FHNW_DARK:   RGB = [30,  30,  30];

const AREA_COLORS: RGB[] = [
  [59,  130, 246],
  [16,  185, 129],
  [245, 158, 11],
  [139, 92,  246],
  [239, 68,  68],
  [20,  184, 166],
  [99,  102, 241],
  [236, 72,  153],
];

function areaColor(i: number): RGB {
  return AREA_COLORS[i % AREA_COLORS.length] ?? [120, 120, 120];
}

// ── Kompetenzstufen-Farbe: grün-basiert relativ zu max ──────────────────────

function levelCell(level: number, max: number) {
  let fill: RGB;
  let text: RGB;
  let fontStyle: 'normal' | 'bold' = 'normal';

  if (level === 0) {
    fill = [210, 210, 210]; text = [150, 150, 150];
  } else if (level >= max) {
    fill = [22, 163, 74]; text = [255, 255, 255]; fontStyle = 'bold';
  } else {
    const r = level / max;
    fill = [
      Math.round(187 - r * 113),
      Math.round(247 - r * 25),
      Math.round(208 - r * 80),
    ];
    text = FHNW_DARK;
  }

  return {
    content: level === 0 ? '–' : `K${level}`,
    styles: { fillColor: fill, textColor: text, fontStyle, halign: 'center' as const },
  };
}

// ── Donut-Sektor ─────────────────────────────────────────────────────────────

function drawSector(
  doc: jsPDF,
  cx: number, cy: number,
  OR: number, IR: number,
  a0: number, a1: number,
  color: RGB,
) {
  const n = Math.max(3, Math.ceil(Math.abs(a1 - a0) / (2 * Math.PI) * 60));
  const pts: [number, number][] = [];
  for (let i = 0; i <= n; i++) {
    const a = a0 + (a1 - a0) * i / n;
    pts.push([cx + OR * Math.cos(a), cy + OR * Math.sin(a)]);
  }
  for (let i = n; i >= 0; i--) {
    const a = a0 + (a1 - a0) * i / n;
    pts.push([cx + IR * Math.cos(a), cy + IR * Math.sin(a)]);
  }
  const dl = pts.slice(1).map((p, i) => [p[0] - pts[i][0], p[1] - pts[i][1]]);
  doc.setFillColor(...color);
  doc.setDrawColor(...color);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (doc as any).lines(dl, pts[0][0], pts[0][1], [1, 1], 'FD', true);
}

// ── Chip-Reihe ────────────────────────────────────────────────────────────────

function chipRow(
  doc: jsPDF,
  chips: string[],
  x0: number, y0: number, x1: number,
  bg: RGB, fg: RGB,
): number {
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7);
  const H = 5, px = 3, gap = 2;
  let cx = x0, cy = y0;
  for (const c of chips) {
    const w = doc.getTextWidth(c) + px * 2;
    if (cx + w > x1 && cx > x0) { cx = x0; cy += H + gap; }
    doc.setFillColor(...bg);
    doc.roundedRect(cx, cy, w, H, 1, 1, 'F');
    doc.setTextColor(...fg);
    doc.text(c, cx + px, cy + 3.5);
    cx += w + gap;
  }
  return cy + H + 3;
}

// ── Bild laden (für FHNW-Logo im Header) ──────────────────────────────────────

export function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload  = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

// ── Hauptfunktion ─────────────────────────────────────────────────────────────

export async function generatePDF(currentUser: User | null, areas: Area[], documents: UserDocument[] = []) {
  if (!currentUser) return;

  const logo = await loadImage('/FHNW_Logo_ohneText.png');

  const doc    = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageW  = doc.internal.pageSize.getWidth();
  const margin = 14;

  // ── Header-Banner ──────────────────────────────────────────────────────────
  const bannerH = 20;
  doc.setFillColor(...FHNW_YELLOW);
  doc.rect(0, 0, pageW, bannerH, 'F');

  // FHNW-Logo links
  const logoH = 10;
  const logoW = logoH * (logo.naturalWidth / logo.naturalHeight);
  doc.addImage(logo, 'PNG', margin, (bannerH - logoH) / 2, logoW, logoH);

  // Titel mit Abstand zum Logo
  doc.setFontSize(14);
  doc.setTextColor(...FHNW_DARK);
  doc.setFont('helvetica', 'bold');
  doc.text('Aufbau von Handlungskompetenzen', margin + logoW + 6, bannerH / 2 + 2);

  // ── Lernenden-Info ─────────────────────────────────────────────────────────
  let y = 30;
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text(currentUser.name, margin, y);

  const specLabel = SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty;
  const ljInfo    = getLehrjahrInfo(currentUser);
  const overall   = getOverallProgress(areas, currentUser.goals);

  y += 6;
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(90, 90, 90);
  doc.text(specLabel, margin, y);

  y += 6;
  doc.setTextColor(...FHNW_DARK);
  doc.text(
    `Lehrjahr: ${ljInfo.current}  |  Lehrzeit: ${ljInfo.pct}% absolviert  |  Gesamtfortschritt: ${overall.achieved}/${overall.total} Leistungsziele (${overall.pct}%)`,
    margin, y,
  );

  // ── Lehrzeit-Balken ────────────────────────────────────────────────────────
  y += 8;
  const bw = (pageW - margin * 2 - (ljInfo.lehrDauer - 1) * 3) / ljInfo.lehrDauer;
  ljInfo.yearPcts.forEach((pct, i) => {
    const bx = margin + i * (bw + 3);
    doc.setFillColor(220, 220, 220);
    doc.roundedRect(bx, y, bw, 5, 1, 1, 'F');
    if (pct > 0) {
      doc.setFillColor(...(pct === 100 ? [52, 211, 153] as RGB : FHNW_YELLOW));
      doc.roundedRect(bx, y, bw * pct / 100, 5, 1, 1, 'F');
    }
    doc.setFontSize(7);
    doc.setTextColor(80, 80, 80);
    doc.text(`${i + 1}. LJ`, bx + bw / 2, y + 9, { align: 'center' });
  });
  y += 16;

  doc.setDrawColor(220, 220, 220);
  doc.line(margin, y, pageW - margin, y);
  y += 8;

  // ── Abschnitt 1: Gesamtfortschritt ───────────────────────────────────────────
  const startY = y;

  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text('Gesamtfortschritt der Leistungszielerreichung', margin, y);
  y += 8;

  // Donut-Chart (links)
  const cx = margin + 22;
  const cy = y + 20;
  const OR = 20, IR = 12;

  const totalGoals = areas.reduce((s, a) =>
    s + a.subComps.reduce((s2, sc) => s2 + sc.goals.length, 0), 0);

  // Grauer Hintergrund-Kreis
  doc.setFillColor(230, 230, 230);
  doc.setDrawColor(230, 230, 230);
  doc.circle(cx, cy, OR, 'F');

  // Farbige Sektoren für erreichte Ziele
  if (totalGoals > 0) {
    let angle = -Math.PI / 2;
    areas.forEach((area, idx) => {
      const achieved = area.subComps.reduce((s, sc) =>
        s + sc.goals.filter(g => (currentUser.goals?.[g.id]?.level ?? 0) >= 1).length, 0);
      if (achieved > 0) {
        const a1 = angle + (achieved / totalGoals) * 2 * Math.PI;
        drawSector(doc, cx, cy, OR, IR, angle, a1, areaColor(idx));
        angle = a1;
      }
    });
  }

  // Weisses Donut-Loch
  doc.setFillColor(255, 255, 255);
  doc.setDrawColor(255, 255, 255);
  doc.circle(cx, cy, IR, 'F');

  // Zentrierter Text
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text(`${overall.pct}%`, cx, cy - 1, { align: 'center' });
  doc.setFontSize(6);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(120, 120, 120);
  doc.text('Gesamt-', cx, cy + 5, { align: 'center' });
  doc.text('fortschritt', cx, cy + 8.5, { align: 'center' });

  // Legende (Bereiche) – rechts vom Donut, volle Seitenbreite verfügbar
  const lx = margin + 46;
  const legendTextW = pageW - margin - lx;
  let ly = startY + 8;
  areas.forEach((area, idx) => {
    const prog = getAreaProgress(area, currentUser.goals);
    const col  = areaColor(idx);
    doc.setFillColor(...col);
    doc.setDrawColor(...col);
    doc.circle(lx + 2, ly, 1.5, 'F');
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...FHNW_DARK);
    const nameShort = doc.splitTextToSize(
      `HK ${area.id.toUpperCase()}: ${area.name}`,
      legendTextW,
    );
    doc.text(nameShort[0] as string, lx + 6, ly + 1);
    ly += 4.5;
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(110, 110, 110);
    doc.text(`${prog.achieved}/${prog.total} Leistungsziele (${prog.pct}%)`, lx + 6, ly);
    ly += 7;
  });

  const notAch = overall.total - overall.achieved;
  if (notAch > 0) {
    doc.setFillColor(200, 200, 200);
    doc.setDrawColor(200, 200, 200);
    doc.circle(lx + 2, ly, 1.5, 'F');
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(130, 130, 130);
    doc.text('Noch nicht erreicht', lx + 6, ly + 1);
    ly += 4.5;
    doc.setFont('helvetica', 'normal');
    doc.text(
      `${notAch}/${overall.total} (${Math.round(notAch / overall.total * 100)}%)`,
      lx + 6, ly,
    );
    ly += 7;
  }

  // Y-Position nach Gesamtfortschritt-Abschnitt
  y = Math.max(cy + OR + 8, ly) + 4;

  // Trennlinie
  doc.setDrawColor(220, 220, 220);
  doc.line(margin, y, pageW - margin, y);
  y += 6;

  // ── Abschnitt 2: Technologien & Systeme ──────────────────────────────────────
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text('Technologien & Systeme', margin, y);
  y += 7;

  const allTechs = [...new Set(documents.flatMap(d => d.technologies ?? []))].sort();
  const allEnvs  = [...new Set(documents.flatMap(d => d.environments  ?? []))].sort();

  if (allTechs.length > 0) {
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(100, 100, 100);
    doc.text('TECHNOLOGIE', margin, y);
    y += 5;
    y = chipRow(doc, allTechs, margin, y, pageW - margin, [219, 234, 254], [30, 64, 175]);
    y += 2;
  }

  if (allEnvs.length > 0) {
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(100, 100, 100);
    doc.text('SYSTEM / UMGEBUNG', margin, y);
    y += 5;
    y = chipRow(doc, allEnvs, margin, y, pageW - margin, [209, 250, 229], [21, 128, 61]);
  }

  y += 4;

  // ── Bereiche (jeder Bereich beginnt auf einer neuen Seite) ───────────────────
  for (const area of areas) {
    const prog = getAreaProgress(area, currentUser.goals);

    doc.addPage();
    y = 20;
    doc.setFillColor(...FHNW_YELLOW);
    doc.rect(margin - 2, y - 4, pageW - margin * 2 + 4, 10, 'F');
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...FHNW_DARK);
    doc.text(`Bereich ${area.id.toUpperCase()}: ${area.name}`, margin, y + 2);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(`${prog.achieved}/${prog.total} (${prog.pct}%)`, pageW - margin, y + 2, { align: 'right' });
    y += 12;

    const rows: object[][] = [];
    for (const sc of area.subComps) {
      rows.push([{
        content: `${sc.id} – ${sc.name}`,
        colSpan: 3,
        styles: { fillColor: [245, 245, 245], fontStyle: 'bold', fontSize: 8, textColor: [50, 50, 50] },
      }]);
      for (const goal of sc.goals) {
        const level = currentUser.goals?.[goal.id]?.level ?? 0;
        rows.push([
          { content: goal.id, styles: { fontSize: 7, textColor: [100, 100, 100], halign: 'center' } },
          { content: goal.description ?? goal.text ?? '', styles: { fontSize: 8 } },
          levelCell(level, goal.max),
        ]);
      }
    }

    autoTable(doc, {
      startY: y,
      head: [[
        { content: 'Nr.',   styles: { halign: 'center' } },
        'Leistungsziel',
        { content: 'Stufe', styles: { halign: 'center' } },
      ]],
      body:   rows,
      columnStyles: {
        0: { cellWidth: 18 },
        1: { cellWidth: 'auto' },
        2: { cellWidth: 22 },
      },
      margin:     { left: margin, right: margin },
      styles:     { fontSize: 8, cellPadding: 2 },
      headStyles: { fillColor: [50, 50, 50], textColor: [255, 255, 255], fontStyle: 'bold' },
      didDrawPage: () => { y = 20; },
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    y = (doc as any).lastAutoTable.finalY + 8;
  }

  // ── Legende ────────────────────────────────────────────────────────────────
  if (y > 260) { doc.addPage(); y = 20; }
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text('Kompetenzstufen (Legende):', margin, y);
  y += 6;
  doc.setFont('helvetica', 'normal');
  const legendItems: { fill: RGB; label: string }[] = [
    { fill: [210, 210, 210], label: '–  Nicht bewertet' },
    { fill: [187, 247, 208], label: 'K1  Niedrigste Stufe (helles Grün)' },
    { fill: [74,  222, 128], label: 'Kn  Zwischenstufen (mittleres Grün)' },
    { fill: [22,  163, 74 ], label: 'Kmax  Max. geforderte Stufe erreicht (klares Grün, fett)' },
  ];
  legendItems.forEach(item => {
    doc.setFillColor(...item.fill);
    doc.roundedRect(margin, y - 3, 8, 4, 1, 1, 'F');
    doc.setTextColor(...FHNW_DARK);
    doc.text(item.label, margin + 10, y);
    y += 6;
  });

  // ── Footer auf jeder Seite ─────────────────────────────────────────────────
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pages = (doc as any).getNumberOfPages() as number;
  for (let p = 1; p <= pages; p++) {
    doc.setPage(p);
    doc.setFontSize(7);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `Erstellt am ${new Date().toLocaleDateString('de-CH')} – FHNW Handlungskompetenz-Tracker`,
      margin, doc.internal.pageSize.getHeight() - 8,
    );
    doc.text(
      `Seite ${p} / ${pages}`,
      pageW - margin, doc.internal.pageSize.getHeight() - 8,
      { align: 'right' },
    );
  }

  doc.save(`Handlungskompetenzen_${currentUser.name.replace(/\s+/g, '_')}.pdf`);
}
