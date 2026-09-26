import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { FHNW_YELLOW, FHNW_DARK, loadImage } from './generatePDF';
import { SPECIALTY_LABEL, getLehrjahrInfo } from '../utils';
import type { User, UserDocument } from '../types';

const BAND_FILL: [number, number, number] = [226, 232, 240];
const BAND_TEXT: [number, number, number] = [51,  65,  85];
const BAND_SUB:  [number, number, number] = [100, 116, 139];

export async function generateLerndokumentationPDF(currentUser: User | null, documents: UserDocument[]) {
  if (!currentUser) return;

  const logo = await loadImage('/FHNW_Logo_ohneText.png');

  const doc     = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
  const pageW   = doc.internal.pageSize.getWidth();
  const pageH   = doc.internal.pageSize.getHeight();
  const margin  = 14;

  // ── Header-Banner ──────────────────────────────────────────────────────────
  const bannerH = 20;
  doc.setFillColor(...FHNW_YELLOW);
  doc.rect(0, 0, pageW, bannerH, 'F');

  const logoH = 10;
  const logoW = logoH * (logo.naturalWidth / logo.naturalHeight);
  doc.addImage(logo, 'PNG', margin, (bannerH - logoH) / 2, logoW, logoH);

  doc.setFontSize(14);
  doc.setTextColor(...FHNW_DARK);
  doc.setFont('helvetica', 'bold');
  doc.text('Lerndokumentation', margin + logoW + 6, bannerH / 2 + 2);

  // ── Lernenden-Info ─────────────────────────────────────────────────────────
  let y = 30;
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...FHNW_DARK);
  doc.text(currentUser.name, margin, y);
  const nameW = doc.getTextWidth(currentUser.name);

  const specLabel = SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty;
  const ljInfo    = getLehrjahrInfo(currentUser);

  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(90, 90, 90);
  doc.text(`   |   ${specLabel}   |   ${ljInfo.current}. Lehrjahr`, margin + nameW, y);

  y += 8;
  doc.setDrawColor(220, 220, 220);
  doc.line(margin, y, pageW - margin, y);
  y += 8;

  if (documents.length === 0) {
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(120, 120, 120);
    doc.text('Keine Dokumente vorhanden.', margin, y);
  }

  const baseW = (pageW - margin * 2) / 4;
  const narrowW = baseW * 2 / 3;
  const wideW   = baseW * 4 / 3;

  for (const d of documents) {
    const hasSub = !!d.description;
    const bandH  = hasSub ? 14 : 10;

    if (y > pageH - 55) { doc.addPage(); y = 20; }

    doc.setFillColor(...BAND_FILL);
    doc.rect(margin - 2, y - 4, pageW - margin * 2 + 4, bandH, 'F');

    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...BAND_TEXT);
    doc.text(d.title, margin, y + 2);

    if (hasSub) {
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...BAND_SUB);
      doc.text(d.description as string, margin, y + 8);
    }

    y += bandH + 1;

    const techs = d.technologies?.length ? d.technologies : ['–'];
    const envs  = d.environments?.length  ? d.environments  : ['–'];

    autoTable(doc, {
      startY: y,
      body: [[
        d.kurzbeschreibung || '–',
        d.umsetzung        || '–',
        '',
        '',
      ]],
      margin:     { left: margin, right: margin },
      styles:     { fontSize: 8, cellPadding: 3, valign: 'top' },
      columnStyles: {
        0: { cellWidth: wideW },
        1: { cellWidth: wideW },
        2: { cellWidth: narrowW },
        3: { cellWidth: narrowW },
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      didDrawCell: (data: any) => {
        if (data.section !== 'body' || (data.column.index !== 2 && data.column.index !== 3)) return;
        const heading = data.column.index === 2 ? 'Technologie' : 'Systeme';
        const items   = data.column.index === 2 ? techs : envs;
        const px = data.cell.x + data.cell.padding('left');
        let py   = data.cell.y + data.cell.padding('top') + 3;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.setTextColor(...FHNW_DARK);
        doc.text(heading, px, py);
        py += 4;
        doc.setFont('helvetica', 'normal');
        items.forEach(item => { doc.text(item, px, py); py += 3.6; });
      },
      didDrawPage: () => { y = 20; },
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    y = (doc as any).lastAutoTable.finalY + 6;
  }

  // ── Footer auf jeder Seite ─────────────────────────────────────────────────
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pages = (doc as any).getNumberOfPages() as number;
  for (let p = 1; p <= pages; p++) {
    doc.setPage(p);
    doc.setFontSize(7);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `Erstellt am ${new Date().toLocaleDateString('de-CH')} – FHNW Handlungskompetenz-Tracker`,
      margin, pageH - 8,
    );
    doc.text(
      `Seite ${p} / ${pages}`,
      pageW - margin, pageH - 8,
      { align: 'right' },
    );
  }

  doc.save(`Lerndokumentation_${currentUser.name.replace(/\s+/g, '_')}.pdf`);
}
