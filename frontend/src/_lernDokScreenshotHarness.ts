import jsPDF from 'jspdf';
import { generateLerndokumentationPDF } from './utils/generateLerndokumentationPDF';
import type { User, UserDocument } from './types';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
(jsPDF as any).API.save = function (this: jsPDF) {
  (window as unknown as { __pdfDataUri: string }).__pdfDataUri = this.output('datauristring');
};

const mockUser: User = {
  id: 'u1', name: 'Heinz Platt', specialty: 'app',
  start_date: '2024-08-10', startDate: '2024-08-10',
  goals: {}, rotations: [],
};

function makeDoc(over: Partial<UserDocument>): UserDocument {
  return {
    id: Math.random().toString(36).slice(2), user_id: 'u1', ap_code: 'SWE', title: 'Titel',
    description: null, kurzbeschreibung: null, umsetzung: null, luecken: null,
    bewertungsart: 'sb', feedback_berufsbildner: null, technologies: [], environments: [],
    document_date: null, file_name: 'x.pdf', content_type: 'application/pdf', file_size: 1,
    uploaded_at: '2025-01-01', goal_links: [],
    ...over,
  };
}

const mockDocuments: UserDocument[] = [
  makeDoc({
    title: 'PBI 39449: Refactoring von Stored Procedures zur Performance-Optimierung langsamer Reports',
    description: 'SWE – Software Engineering, Sprint 14',
    kurzbeschreibung: 'Die bestehenden Reporting-Prozeduren wiesen bei grossen Datenmengen erhebliche Laufzeitprobleme auf. Ziel war es, die Abfragen zu analysieren und gezielt zu optimieren, ohne die fachliche Logik zu verändern.',
    umsetzung: 'Mittels Execution Plans wurden Engpässe identifiziert (fehlende Indizes, Table Scans). Es wurden neue nicht-gruppierte Indizes angelegt, Subqueries durch JOINs ersetzt und temporäre Tabellen eingeführt. Die Laufzeit sank von ca. 40s auf unter 2s.',
    technologies: ['T-SQL', 'SQL Server'],
    environments: ['Microsoft SQL Server', 'Azure DevOps'],
  }),
  makeDoc({
    title: 'IPA-Bericht_AltinSherifi',
    kurzbeschreibung: 'Individuelle praktische Arbeit zur Erstellung einer internen Webanwendung zur Ressourcenplanung.',
    umsetzung: 'Umsetzung mit React-Frontend und FastAPI-Backend, Deployment über Azure DevOps Pipelines.',
    technologies: ['Python', 'FastAPI', 'JavaScript'],
    environments: ['Azure DevOps', 'Ubuntu'],
  }),
  makeDoc({
    title: 'IPA_FlorianKohler',
    description: 'Fachrichtung Applikationsentwicklung',
    kurzbeschreibung: 'Automatisierung von Salt-States zur Konfiguration von Windows- und Linux-Clients im Betrieb.',
    umsetzung: 'Erstellung und Test von SaltStack-States, Rollout über Salt Master, Dokumentation im Wiki.',
    technologies: ['Salt', 'SaltStack'],
    environments: ['Salt Master', 'Windows'],
  }),
];

(window as unknown as { runLernDokScreenshot: () => Promise<string> }).runLernDokScreenshot = async () => {
  await generateLerndokumentationPDF(mockUser, mockDocuments);
  return (window as unknown as { __pdfDataUri: string }).__pdfDataUri;
};
