import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { BLOOM, SPECIALTY_LABEL, getLehrjahrInfo, getAreaProgress, getOverallProgress } from '../utils';
import type { User, Area } from '../types';

type RGB = [number, number, number];

const FHNW_YELLOW: RGB = [253, 231, 14];
const FHNW_DARK:   RGB = [30,  30,  30];
const LEVEL_COLORS: Record<number, RGB> = {
  0: [200, 200, 200],
  1: [96,  165, 250],
  2: [52,  211, 153],
  3: [163, 230, 53],
  4: [251, 191, 36],
  5: [249, 115, 22],
  6: [168, 85,  247],
};

function levelCell(level: number, max: number) {
  const achieved = level >= max;
  const label    = level === 0 ? '–' : `K${level}`;
  return {
    content: label,
    styles: {
      fillColor:  achieved ? (LEVEL_COLORS[level] ?? [200, 200, 200]) : [240, 240, 240],
      textColor:  achieved ? FHNW_DARK : [150, 150, 150],
      fontStyle:  achieved ? 'bold' : 'normal',
      halign:     'center' as const,
    },
  };
}

export function generatePDF(currentUser: User | null, areas: Area[]) {
  if (!currentUser) return;

  const doc   = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  const margin = 14;

  // Header-Banner
  doc.setFillColor(...FHNW_YELLOW);
  doc.rect(0, 0, pageW, 22, 'F');
  doc.setFontSize(14);
  doc.setTextColor(...FHNW_DARK);
  doc.setFont('helvetica', 'bold');
  doc.text('Handlungskompetenz-Tracker', margin, 14);

  const specLabel = SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty;
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.text(specLabel, pageW - margin, 14, { align: 'right' });

  // Lernenden-Info
  let y = 30;
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text(currentUser.name, margin, y);

  const ljInfo  = getLehrjahrInfo(currentUser);
  const overall = getOverallProgress(areas, currentUser.goals);

  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  y += 6;
  doc.text(
    `Lehrjahr: ${ljInfo.current}  |  Lehrzeit: ${ljInfo.pct}% absolviert  |  Gesamtfortschritt: ${overall.achieved}/${overall.total} Leistungsziele (${overall.pct}%)`,
    margin, y
  );

  // Lehrzeit-Balken
  y += 8;
  const barW = (pageW - margin * 2 - (ljInfo.lehrDauer - 1) * 3) / ljInfo.lehrDauer;
  ljInfo.yearPcts.forEach((pct, i) => {
    const x = margin + i * (barW + 3);
    doc.setFillColor(220, 220, 220);
    doc.roundedRect(x, y, barW, 5, 1, 1, 'F');
    if (pct > 0) {
      if (pct === 100) doc.setFillColor(52, 211, 153);
      else             doc.setFillColor(...FHNW_YELLOW);
      doc.roundedRect(x, y, barW * pct / 100, 5, 1, 1, 'F');
    }
    doc.setFontSize(7);
    doc.setTextColor(80, 80, 80);
    doc.text(`${i + 1}. LJ`, x + barW / 2, y + 9, { align: 'center' });
  });
  y += 16;

  doc.setDrawColor(220, 220, 220);
  doc.line(margin, y, pageW - margin, y);
  y += 6;

  // Bereiche
  for (const area of areas) {
    const prog = getAreaProgress(area, currentUser.goals);

    if (y > 260) { doc.addPage(); y = 20; }
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
        const goalData = currentUser.goals?.[goal.id] ?? { level: 0, comment: '' };
        const level = goalData.level ?? 0;
        rows.push([
          { content: goal.id, styles: { fontSize: 7, textColor: [100, 100, 100], halign: 'center' } },
          { content: goal.description ?? goal.text ?? '', styles: { fontSize: 8 } },
          levelCell(level, goal.max),
        ]);
      }
    }

    autoTable(doc, {
      startY: y,
      head:   [[
        { content: 'Nr.',         styles: { halign: 'center' } },
        'Leistungsziel',
        { content: 'Stufe',       styles: { halign: 'center' } },
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      didDrawPage: () => { y = 20; },
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    y = (doc as any).lastAutoTable.finalY + 8;
  }

  // Legende
  if (y > 250) { doc.addPage(); y = 20; }
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text('Kompetenzstufen:', margin, y);
  y += 5;
  doc.setFont('helvetica', 'normal');
  BLOOM.forEach((label, i) => {
    if (i === 0) return;
    const [r, g, b] = LEVEL_COLORS[i] ?? ([200, 200, 200] as RGB);
    doc.setFillColor(r, g, b);
    doc.roundedRect(margin, y - 3, 8, 4, 1, 1, 'F');
    doc.setTextColor(...FHNW_DARK);
    doc.text(`K${i} – ${label}`, margin + 10, y);
    y += 6;
  });

  // Footer
  const pages = doc.internal.getNumberOfPages();
  for (let p = 1; p <= pages; p++) {
    doc.setPage(p);
    doc.setFontSize(7);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `Erstellt am ${new Date().toLocaleDateString('de-CH')} – Handlungskompetenz-Tracker FHNW`,
      margin, doc.internal.pageSize.getHeight() - 8
    );
    doc.text(`Seite ${p} / ${pages}`, pageW - margin, doc.internal.pageSize.getHeight() - 8, { align: 'right' });
  }

  const safeName = currentUser.name.replace(/\s+/g, '_');
  doc.save(`Handlungskompetenzen_${safeName}.pdf`);
}
