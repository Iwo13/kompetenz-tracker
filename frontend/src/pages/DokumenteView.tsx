import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { api } from '../api/client';
import { generateLerndokumentationPDF } from '../utils/generateLerndokumentationPDF';
import type { UserDocument, BloomLevel, DocumentGoalLink } from '../types';

const BLOOM_LABELS = ['K0 – Keine', 'K1 – Wissen', 'K2 – Verstehen', 'K3 – Anwenden', 'K4 – Analysieren', 'K5 – Synthese', 'K6 – Beurteilen'];

function todayIso() {
  return new Date().toISOString().split('T')[0];
}
function isoToDisplay(iso: string | null | undefined) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString('de-CH', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
function isoToDateInput(iso: string | null | undefined) {
  if (!iso) return '';
  return iso.split('T')[0];
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('de-CH', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function fileIcon(contentType: string) {
  if (contentType.includes('pdf'))   return '📄';
  if (contentType.includes('image')) return '🖼';
  if (contentType.includes('word') || contentType.includes('document')) return '📝';
  if (contentType.includes('sheet') || contentType.includes('excel'))   return '📊';
  return '📎';
}

// ── Upload Modal ────────────────────────────────────────────────────────────────
interface UploadModalProps {
  userId: string;
  activeApCode: string | null;
  onClose: () => void;
  onUploaded: (doc: UserDocument) => void;
}

function UploadModal({ userId, activeApCode, onClose, onUploaded }: UploadModalProps) {
  const { uploadDocument, ausbildungsplaetze, currentUser } = useApp();
  const fileRef = useRef<HTMLInputElement>(null);
  const [title,      setTitle]      = useState('');
  const [untertitel, setUntertitel] = useState('');
  const [apCode,     setApCode]     = useState(activeApCode ?? '');
  const [docDate,    setDocDate]    = useState(todayIso());
  const [file,          setFile]          = useState<File | null>(null);
  const [saving,        setSaving]        = useState(false);
  const [error,         setError]         = useState<string | null>(null);

  const userApCodes  = [...new Set(currentUser?.rotations.map(r => r.ap_code) ?? [])];
  const availableAPs = ausbildungsplaetze.filter(ap => userApCodes.includes(ap.code));

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    if (f && !title) setTitle(f.name.replace(/\.[^.]+$/, ''));
  }

  async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!file)   { setError('Bitte eine Datei wählen.'); return; }
    if (!apCode) { setError('Bitte einen Ausbildungsplatz wählen.'); return; }
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('title', title.trim() || file.name);
      fd.append('apCode', apCode);
      fd.append('documentDate', docDate);
      if (untertitel.trim()) fd.append('description', untertitel.trim());
      const uploaded = await uploadDocument(userId, fd);
      onUploaded(uploaded);
      onClose();
    } catch {
      setError('Fehler beim Hochladen. Bitte erneut versuchen.');
    } finally {
      setSaving(false);
    }
  }

  const modal = (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="upload-modal" onClick={e => e.stopPropagation()}>
        <div className="upload-modal-header">
          <h2 className="upload-modal-title">Neues Dokument</h2>
          <button className="upload-modal-close" onClick={onClose} type="button">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="upload-modal-form">
          <div className="upload-field">
            <label className="upload-label">Datei *</label>
            <input ref={fileRef} type="file" onChange={handleFileChange} className="upload-file-input" />
          </div>
          <div className="upload-field">
            <label className="upload-label">Titel *</label>
            <input className="upload-input" value={title} onChange={e => setTitle(e.target.value)}
              placeholder="Titel des Dokuments" required />
          </div>
          <div className="upload-field">
            <label className="upload-label">Untertitel</label>
            <input className="upload-input" value={untertitel} onChange={e => setUntertitel(e.target.value)}
              placeholder="Zusatztext für zweite Zeile (optional)" />
          </div>
          <div className="upload-field">
            <label className="upload-label">Datum des Dokuments</label>
            <input type="date" className="upload-input upload-date-input"
              value={docDate} onChange={e => setDocDate(e.target.value)} />
          </div>
          <div className="upload-field">
            <label className="upload-label">Ausbildungsplatz *</label>
            <select className="upload-input" value={apCode} onChange={e => setApCode(e.target.value)} required>
              <option value="">– Bitte wählen –</option>
              {availableAPs.map(ap => (
                <option key={ap.code} value={ap.code}>{ap.code} – {ap.name}</option>
              ))}
            </select>
          </div>
          {error && <p className="upload-error">{error}</p>}
          <div className="upload-modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Abbrechen</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Wird hochgeladen…' : 'Hochladen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

// ── Leistungsziele-Modal ───────────────────────────────────────────────────────
interface LeistungszieleModalProps {
  doc: UserDocument;
  userId: string;
  areas: import('../types').Area[];
  onClose: () => void;
  onSaved: (newGoalIds: string[], updatedDoc: Partial<UserDocument>) => void;
  // current text field values from DocRow to avoid overwriting them
  kurzbeschreibung: string;
  umsetzung: string;
  luecken: string;
  feedbackBerufsbildner: string;
}

function LeistungszieleModal({ doc, userId, areas, onClose, onSaved, kurzbeschreibung, umsetzung, luecken, feedbackBerufsbildner }: LeistungszieleModalProps) {
  const { updateDocument, ausbildungsplaetze, currentUser } = useApp();
  const [title,         setTitle]         = useState(doc.title);
  const [untertitel,    setUntertitel]    = useState(doc.description ?? '');
  const [apCode,        setApCode]        = useState(doc.ap_code);
  const [docDate,       setDocDate]       = useState(isoToDateInput(doc.document_date) || todayIso());
  const [selectedGoals, setSelectedGoals] = useState<Set<string>>(new Set(doc.goal_links.map(l => l.goal_id)));
  const [openAreas,     setOpenAreas]     = useState<Set<string>>(new Set());
  const [saving,        setSaving]        = useState(false);
  const [error,         setError]         = useState<string | null>(null);

  const userApCodes  = [...new Set(currentUser?.rotations.map(r => r.ap_code) ?? [])];
  const availableAPs = ausbildungsplaetze.filter(ap => userApCodes.includes(ap.code));

  function toggleGoal(id: string) {
    setSelectedGoals(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }
  function toggleArea(areaId: string) {
    setOpenAreas(prev => { const n = new Set(prev); n.has(areaId) ? n.delete(areaId) : n.add(areaId); return n; });
  }

  async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    try {
      await updateDocument(userId, doc.id, {
        title: title.trim(),
        description: untertitel.trim() || undefined,
        ap_code: apCode,
        goal_ids: [...selectedGoals],
        kurzbeschreibung:       kurzbeschreibung       || undefined,
        umsetzung:              umsetzung              || undefined,
        luecken:                luecken                || undefined,
        feedback_berufsbildner: feedbackBerufsbildner  || undefined,
        document_date:          docDate                || undefined,
      });
      onSaved([...selectedGoals], { title: title.trim(), description: untertitel.trim() || null, ap_code: apCode });
      onClose();
    } catch {
      setError('Fehler beim Speichern.');
    } finally {
      setSaving(false);
    }
  }

  const modal = (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="upload-modal" onClick={e => e.stopPropagation()}>
        <div className="upload-modal-header">
          <h2 className="upload-modal-title">Leistungsziele zur Bewertung auswählen</h2>
          <button className="upload-modal-close" onClick={onClose} type="button">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="upload-modal-form">
          <div className="upload-field">
            <label className="upload-label">Titel *</label>
            <input className="upload-input" value={title} onChange={e => setTitle(e.target.value)} required />
          </div>
          <div className="upload-field">
            <label className="upload-label">Untertitel</label>
            <input className="upload-input" value={untertitel} onChange={e => setUntertitel(e.target.value)}
              placeholder="Zusatztext (optional)" />
          </div>
          <div className="upload-field">
            <label className="upload-label">Datum des Dokuments</label>
            <input type="date" className="upload-input upload-date-input"
              value={docDate} onChange={e => setDocDate(e.target.value)} />
          </div>
          <div className="upload-field">
            <label className="upload-label">Ausbildungsplatz *</label>
            <select className="upload-input" value={apCode} onChange={e => setApCode(e.target.value)} required>
              {availableAPs.map(ap => (
                <option key={ap.code} value={ap.code}>{ap.code} – {ap.name}</option>
              ))}
            </select>
          </div>
          <div className="upload-field">
            <label className="upload-label">
              Verknüpfte Handlungskompetenzen
              {selectedGoals.size > 0 && <span className="upload-hk-count"> ({selectedGoals.size} gewählt)</span>}
            </label>
            <div className="upload-hk-container">
              {areas.map(area => {
                const areaGoals = area.subComps.flatMap(sc => sc.goals);
                const selectedInArea = areaGoals.filter(g => selectedGoals.has(g.id)).length;
                const isOpen = openAreas.has(area.id);
                return (
                  <div key={area.id} className="upload-hk-area">
                    <button type="button" className="upload-hk-area-header" onClick={() => toggleArea(area.id)}>
                      <span className="upload-hk-area-toggle">{isOpen ? '▼' : '▶'}</span>
                      <span className="upload-hk-area-name">{area.id.toUpperCase()} – {area.name}</span>
                      {selectedInArea > 0 && <span className="upload-hk-badge">{selectedInArea}</span>}
                    </button>
                    {isOpen && (
                      <div className="upload-hk-goals">
                        {area.subComps.map(sc => (
                          <div key={sc.id}>
                            <div className="upload-hk-subcomp">{sc.name}</div>
                            {sc.goals.map(g => (
                              <label key={g.id} className="upload-hk-goal">
                                <input type="checkbox" checked={selectedGoals.has(g.id)} onChange={() => toggleGoal(g.id)} />
                                <span><strong>{g.id.toUpperCase()}</strong> – {g.text ?? g.id}</span>
                              </label>
                            ))}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          {error && <p className="upload-error">{error}</p>}
          <div className="upload-modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Abbrechen</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Wird gespeichert…' : 'Speichern'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
  return createPortal(modal, document.body);
}

// ── Dokument-Zeile (Accordion) ─────────────────────────────────────────────────
interface DocRowProps {
  doc: UserDocument;
  userId: string;
  areas: import('../types').Area[];
  isOpen: boolean;
  onToggle: () => void;
  onDelete: (docId: string) => void;
}

function DocRow({ doc, userId, areas, isOpen: open, onToggle, onDelete }: DocRowProps) {
  const { updateDocumentGoal, updateDocument, reloadGoals, aiEvaluateDocument, currentUser, role, ausbildungsplaetze } = useApp();
  const navigate = useNavigate();
  const apFullName = ausbildungsplaetze.find(ap => ap.code === doc.ap_code)?.name;
  const [showEdit,        setShowEdit]        = useState(false);
  const [saving,          setSaving]          = useState<string | null>(null);
  const [savingBewertung, setSavingBewertung] = useState(false);
  const [savedOk,         setSavedOk]         = useState(false);
  const [aiLoading,       setAiLoading]       = useState(false);
  const [aiError,         setAiError]         = useState<string | null>(null);
  const [aiTokens,        setAiTokens]        = useState<{ prompt: number; completion: number; total: number } | null>(null);
  const [pendingDelete,   setPendingDelete]   = useState<Set<string>>(new Set());
  const [deletingGoal,    setDeletingGoal]    = useState<string | null>(null);
  const [localLinks, setLocalLinks] = useState(
    [...doc.goal_links].sort((a, b) => a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }))
  );

  // Textfelder mit Autosave
  const [kurzbeschreibung,       setKurzbeschreibung]       = useState(doc.kurzbeschreibung ?? '');
  const [umsetzung,              setUmsetzung]              = useState(doc.umsetzung ?? '');
  const [luecken,                setLuecken]                = useState(doc.luecken ?? '');
  const [feedbackBerufsbildner,  setFeedbackBerufsbildner]  = useState(doc.feedback_berufsbildner ?? '');
  const savingTextRef = useRef(false);

  // Sync local state when AI evaluation updates the doc prop
  useEffect(() => { setKurzbeschreibung(doc.kurzbeschreibung ?? ''); }, [doc.kurzbeschreibung]);
  useEffect(() => { setUmsetzung(doc.umsetzung ?? ''); },             [doc.umsetzung]);
  useEffect(() => { setLuecken(doc.luecken ?? ''); },                 [doc.luecken]);
  useEffect(() => { setFeedbackBerufsbildner(doc.feedback_berufsbildner ?? ''); }, [doc.feedback_berufsbildner]);
  useEffect(() => {
    setLocalLinks([...doc.goal_links].sort((a, b) => a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true })));
  }, [doc.goal_links.length]);

  const areaBadges = [...new Set(localLinks.map(l => l.goal_id[0].toUpperCase()))].sort();

  const goalMap = new Map(areas.flatMap(a => a.subComps.flatMap(sc =>
    sc.goals.map(g => [g.id, { text: g.text ?? g.id, max: g.max }])
  )));

  async function saveTextFields(overrides?: { kurzbeschreibung?: string; umsetzung?: string; luecken?: string; feedbackBerufsbildner?: string }) {
    if (savingTextRef.current) return;
    savingTextRef.current = true;
    try {
      await updateDocument(userId, doc.id, {
        title:       doc.title,
        description: doc.description ?? undefined,
        ap_code:     doc.ap_code,
        goal_ids:    localLinks.map(l => l.goal_id),
        document_date: isoToDateInput(doc.document_date) || undefined,
        kurzbeschreibung:      overrides?.kurzbeschreibung      !== undefined ? overrides.kurzbeschreibung      || undefined : kurzbeschreibung      || undefined,
        umsetzung:             overrides?.umsetzung             !== undefined ? overrides.umsetzung             || undefined : umsetzung             || undefined,
        luecken:               overrides?.luecken               !== undefined ? overrides.luecken               || undefined : luecken               || undefined,
        feedback_berufsbildner: overrides?.feedbackBerufsbildner !== undefined ? overrides.feedbackBerufsbildner || undefined : feedbackBerufsbildner || undefined,
      });
    } finally {
      savingTextRef.current = false;
    }
  }

  async function handleGoalUpdate(goalId: string, field: 'einschaetzung' | 'bloom_level', value: string | number | null) {
    const link = localLinks.find(l => l.goal_id === goalId);
    if (!link) return;
    if (field === 'bloom_level' && value === -1) {
      setPendingDelete(prev => new Set(prev).add(goalId));
      return;
    }
    const newEinschaetzung = field === 'einschaetzung' ? (value as string | null) : link.einschaetzung;
    const newBloom = field === 'bloom_level' ? (value as number | null) : link.bloom_level;
    setLocalLinks(prev => prev.map(l => l.goal_id === goalId
      ? { ...l, einschaetzung: newEinschaetzung, bloom_level: newBloom } : l));
    if (field === 'bloom_level') {
      setSaving(goalId);
      try { await updateDocumentGoal(userId, doc.id, goalId, newEinschaetzung, newBloom); }
      finally { setSaving(null); }
    }
  }

  async function handleConfirmDelete(goalId: string) {
    setDeletingGoal(goalId);
    try {
      const remainingIds = localLinks.filter(l => l.goal_id !== goalId).map(l => l.goal_id);
      await updateDocument(userId, doc.id, {
        title: doc.title, description: doc.description ?? undefined, ap_code: doc.ap_code,
        goal_ids: remainingIds, kurzbeschreibung: kurzbeschreibung || undefined,
        umsetzung: umsetzung || undefined, luecken: luecken || undefined,
      });
      setLocalLinks(prev => prev.filter(l => l.goal_id !== goalId));
      setPendingDelete(prev => { const s = new Set(prev); s.delete(goalId); return s; });
      await reloadGoals(userId);
    } finally {
      setDeletingGoal(null);
    }
  }

  async function handleEinschaetzungBlur(goalId: string) {
    const link = localLinks.find(l => l.goal_id === goalId);
    if (!link) return;
    setSaving(goalId);
    try { await updateDocumentGoal(userId, doc.id, goalId, link.einschaetzung, link.bloom_level); }
    finally { setSaving(null); }
  }

  function handleLeistungszieleModalSaved(newGoalIds: string[], updatedDoc: Partial<UserDocument>) {
    setLocalLinks(prev => {
      const prevMap = new Map(prev.map(l => [l.goal_id, l]));
      return newGoalIds
        .map(id => prevMap.get(id) ?? { id: '', goal_id: id, bloom_level: 1, einschaetzung: null } as DocumentGoalLink)
        .sort((a, b) => a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }));
    });
    // Reflect title/untertitel changes immediately in the header via context (updateDocument already updated context)
    void updatedDoc;
    setShowEdit(false);
  }

  async function handleAiEvaluate() {
    if (!currentUser) return;
    setAiLoading(true);
    setAiError(null);
    setAiTokens(null);
    try {
      const res = await aiEvaluateDocument(currentUser.id, doc.id);
      const updated = res.document;
      setKurzbeschreibung(updated.kurzbeschreibung ?? '');
      setUmsetzung(updated.umsetzung ?? '');
      setLuecken(updated.luecken ?? '');
      setLocalLinks(
        [...updated.goal_links].sort((a, b) =>
          a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }))
      );
      setAiTokens({ prompt: res.prompt_tokens, completion: res.completion_tokens, total: res.total_tokens });
    } catch {
      setAiError('AI-Analyse fehlgeschlagen. Bitte Konfiguration prüfen.');
    } finally {
      setAiLoading(false);
    }
  }

  async function handleSaveBewertung() {
    if (!currentUser) return;
    setSavingBewertung(true);
    setSavedOk(false);
    try {
      await reloadGoals(userId);
      setSavedOk(true);
      setTimeout(() => setSavedOk(false), 3000);
    } finally {
      setSavingBewertung(false);
    }
  }

  return (
    <>
      <div className={`doc-row${open ? ' open' : ''}`}>
        {/* Header */}
        <button className="doc-row-header" onClick={onToggle}>
          <span className="doc-icon">{fileIcon(doc.content_type)}</span>
          <div className="doc-row-meta">
            <span className="doc-title">{doc.title}</span>
            {doc.description && <span className="doc-desc">{doc.description}</span>}
          </div>
          {areaBadges.length > 0 && (
            <div className="doc-area-badges">
              {areaBadges.map(a => <span key={a} className="doc-area-badge">{a}</span>)}
            </div>
          )}
          {feedbackBerufsbildner && (
            <img src="/IconKommentiert.png" alt="Feedback vorhanden" title="Feedback vorhanden"
              style={{ width: 22, height: 22, objectFit: 'contain', alignSelf: 'center', flexShrink: 0 }} />
          )}
          <span className="doc-ap-badge" title={apFullName}>{doc.ap_code}</span>
          <span className="doc-date">{isoToDisplay(doc.document_date) ?? formatDate(doc.uploaded_at)}</span>
          <span className="accordion-icon">{open ? '×' : '+'}</span>
        </button>

        {/* Body */}
        {open && (
          <div className="doc-row-body">
            {/* Toolbar */}
            <div className="doc-toolbar">
              <a href={api.getDocumentFileUrl(userId, doc.id)}
                target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ fontSize: 13 }}>
                ⬇ Datei öffnen
              </a>
              <button className="btn btn-secondary" style={{ fontSize: 13 }}
                onClick={() => setShowEdit(true)}>
                ✎ Leistungsziele zur Bewertung ändern
              </button>
              <button className="btn btn-secondary" style={{ fontSize: 13, borderColor: '#7c3aed', color: '#7c3aed' }}
                onClick={handleAiEvaluate}
                disabled={aiLoading}
                title="Die Bewertung erfolgt durch GPT-Modelle, betrieben im Azure-Tenant der FHNW. Es werden nur leere Felder automatisch gefüllt.">
                {aiLoading ? <><span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>{' '}AI analysiert…</> : '✦ Bewertung durch AI'}
              </button>
              <button className="btn btn-primary" style={{ fontSize: 13 }}
                onClick={handleSaveBewertung}
                disabled={savingBewertung || localLinks.length === 0}>
                {savingBewertung ? 'Wird gespeichert…' : savedOk ? '✓ Gespeichert' : 'Bewertung Speichern'}
              </button>
              <span style={{ flex: 1 }} />
              <button className="btn btn-secondary" style={{ fontSize: 12, color: '#dc2626', borderColor: '#dc2626' }}
                onClick={() => onDelete(doc.id)}>
                🗑 Löschen
              </button>
            </div>
            {aiError && (
              <p style={{ color: '#dc2626', fontSize: 13, margin: '6px 0 0' }}>{aiError}</p>
            )}
            {aiTokens && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 12,
                background: '#f0fdf4', border: '1px solid #86efac', borderRadius: 6,
                padding: '6px 12px', marginTop: 6, fontSize: 12, color: '#166534',
              }}>
                <span>✦ AI-Bewertung abgeschlossen</span>
                <span>Prompt: <strong>{aiTokens.prompt.toLocaleString()}</strong></span>
                <span>Antwort: <strong>{aiTokens.completion.toLocaleString()}</strong></span>
                <span>Total: <strong>{aiTokens.total.toLocaleString()}</strong> Tokens</span>
                <button onClick={() => setAiTokens(null)} style={{
                  marginLeft: 'auto', background: 'none', border: 'none',
                  cursor: 'pointer', color: '#166534', fontSize: 14, lineHeight: 1,
                }}>✕</button>
              </div>
            )}

            {/* Feedback Berufsbildner/in */}
            {role === 'berufsbildner' ? (
              <div style={{ margin: '12px 0 4px' }}>
                <label className="doc-text-label">Feedback Berufsbildner/in</label>
                <textarea className="doc-text-area"
                  rows={3}
                  style={{ background: '#eff6ff', borderColor: '#93c5fd' }}
                  value={feedbackBerufsbildner}
                  onChange={e => setFeedbackBerufsbildner(e.target.value)}
                  onBlur={() => saveTextFields({ feedbackBerufsbildner })}
                  placeholder="Feedback, Lob oder Hinweise für den Lernenden…" />
              </div>
            ) : feedbackBerufsbildner ? (
              <div style={{ margin: '12px 0 4px', padding: '10px 14px', background: '#eff6ff', border: '1px solid #93c5fd', borderRadius: 6 }}>
                <div className="doc-text-label" style={{ marginBottom: 4 }}>Feedback Berufsbildner/in</div>
                <p style={{ margin: 0, fontSize: 14, whiteSpace: 'pre-wrap' }}>{feedbackBerufsbildner}</p>
              </div>
            ) : null}

            {/* Technologie + System Chips */}
            {((doc.technologies?.length ?? 0) > 0 || (doc.environments?.length ?? 0) > 0) && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, margin: '10px 0 4px' }}>
                {doc.technologies?.map(t => (
                  <button key={t} onClick={() => navigate(`/dokumente?tag=${encodeURIComponent(t)}`)}
                    style={{ background: '#dbeafe', color: '#1e40af', borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', border: 'none' }}
                    title={`Alle Dokumente mit «${t}» anzeigen`}>{t}</button>
                ))}
                {doc.environments?.map(e => (
                  <button key={e} onClick={() => navigate(`/dokumente?tag=${encodeURIComponent(e)}`)}
                    style={{ background: '#dcfce7', color: '#166534', borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', border: 'none' }}
                    title={`Alle Dokumente mit «${e}» anzeigen`}>{e}</button>
                ))}
              </div>
            )}

            {/* Textfelder */}
            <div className="doc-text-fields">
              <div className="doc-text-field">
                <label className="doc-text-label">Kurzbeschreibung</label>
                <textarea className="doc-text-area" rows={6}
                  value={kurzbeschreibung}
                  onChange={e => setKurzbeschreibung(e.target.value)}
                  onBlur={() => saveTextFields({ kurzbeschreibung })}
                  placeholder="Beschreibung des Inhalts in 4/5 Sätzen. Was deckt es ab (Problemstellung, Funktion, Ergebnis)" />
              </div>
              <div className="doc-text-field">
                <label className="doc-text-label">Umsetzung der Arbeit</label>
                <textarea className="doc-text-area" rows={6}
                  value={umsetzung}
                  onChange={e => setUmsetzung(e.target.value)}
                  onBlur={() => saveTextFields({ umsetzung })}
                  placeholder="Wie wurde die Problemstellung gelöst, wie ist das Vorgehen und die Dokumentation." />
              </div>
              <div className="doc-text-field">
                <label className="doc-text-label">Lücken und Verbesserungsmöglichkeiten</label>
                <textarea className="doc-text-area" rows={6}
                  value={luecken}
                  onChange={e => setLuecken(e.target.value)}
                  onBlur={() => saveTextFields({ luecken })}
                  placeholder="Was könnte bei der nächsten Arbeit dieser Art berücksichtigt werden." />
              </div>
            </div>

            {/* Leistungsziel-Tabelle */}
            {localLinks.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 12 }}>
                {aiTokens
                  ? 'Die KI konnte in diesem Dokument keine passenden Leistungsziele erkennen. Bitte «Leistungsziele zur Bewertung ändern» verwenden, um Ziele manuell zu verknüpfen.'
                  : 'Keine Leistungsziele verknüpft. Bitte «Leistungsziele zur Bewertung ändern» verwenden.'}
              </p>
            ) : (
              <table className="doc-goal-table">
                <thead>
                  <tr>
                    <th>Leistungsziel</th>
                    <th>Beschreibung</th>
                    <th style={{ width: '35%' }}>Kommentar/Notiz...</th>
                    <th>Kompetenzstufe</th>
                  </tr>
                </thead>
                <tbody>
                  {localLinks.map(link => {
                    const gInfo    = goalMap.get(link.goal_id);
                    const currentLevel = currentUser?.goals[link.goal_id]?.level ?? 0;
                    const isSaving = saving === link.goal_id;
                    return (
                      <tr key={link.goal_id}
                        style={pendingDelete.has(link.goal_id) ? { background: '#fef2f2' } : undefined}>
                        <td><strong>{link.goal_id.toUpperCase()}</strong></td>
                        <td style={{ fontSize: 12 }}>{gInfo?.text ?? link.goal_id}</td>
                        {pendingDelete.has(link.goal_id) ? (
                          <td colSpan={2}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '4px 0' }}>
                              <span style={{ fontSize: 13, color: '#dc2626' }}>Leistungsziel wirklich löschen?</span>
                              <button className="btn btn-primary"
                                style={{ fontSize: 12, background: '#dc2626', borderColor: '#dc2626' }}
                                disabled={deletingGoal === link.goal_id}
                                onClick={() => handleConfirmDelete(link.goal_id)}>
                                {deletingGoal === link.goal_id ? '…' : 'OK, löschen'}
                              </button>
                              <button className="btn btn-secondary" style={{ fontSize: 12 }}
                                onClick={() => setPendingDelete(prev => { const s = new Set(prev); s.delete(link.goal_id); return s; })}>
                                Abbrechen
                              </button>
                            </div>
                          </td>
                        ) : (
                          <>
                            <td>
                              <textarea className="doc-einschaetzung" rows={2}
                                value={link.einschaetzung ?? ''}
                                onChange={e => handleGoalUpdate(link.goal_id, 'einschaetzung', e.target.value)}
                                onBlur={() => handleEinschaetzungBlur(link.goal_id)}
                                placeholder="Kommentar/Notiz…" />
                            </td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <select className="doc-bloom-select" disabled={isSaving}
                                  value={link.bloom_level ?? currentLevel}
                                  onChange={e => handleGoalUpdate(link.goal_id, 'bloom_level', Number(e.target.value))}>
                                  {([1,2,3,4,5,6] as BloomLevel[]).map(l => (
                                    <option key={l} value={l}>{BLOOM_LABELS[l]}</option>
                                  ))}
                                  <option value={-1} style={{ color: '#dc2626' }}>— Leistungsziel entfernen</option>
                                </select>
                                {isSaving && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>…</span>}
                              </div>
                            </td>
                          </>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      {showEdit && (
        <LeistungszieleModal doc={doc} userId={userId} areas={areas}
          onClose={() => setShowEdit(false)} onSaved={handleLeistungszieleModalSaved}
          kurzbeschreibung={kurzbeschreibung} umsetzung={umsetzung} luecken={luecken}
          feedbackBerufsbildner={feedbackBerufsbildner} />
      )}
    </>
  );
}

// ── Haupt-View ─────────────────────────────────────────────────────────────────
export default function DokumenteView() {
  const { currentUser, documents, deleteDocument, areas, activeAP } = useApp();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showUpload, setShowUpload] = useState(false);
  const [openDocId,  setOpenDocId]  = useState<string | null>(null);

  const tagFilter = searchParams.get('tag');

  useEffect(() => {
    const openId = searchParams.get('open');
    if (openId) setOpenDocId(openId);
  }, [searchParams]);

  if (!currentUser) {
    return (
      <div className="no-user-state">
        <h3>Kein Lernender ausgewählt</h3>
        <p>Bitte links einen Lernenden auswählen.</p>
      </div>
    );
  }

  async function handleDelete(docId: string) {
    if (!confirm('Dokument wirklich löschen?')) return;
    await deleteDocument(currentUser!.id, docId);
    if (openDocId === docId) setOpenDocId(null);
  }

  const allTechs = [...new Set(documents.filter(Boolean).flatMap(d => d.technologies ?? []))].sort();
  const allEnvs  = [...new Set(documents.filter(Boolean).flatMap(d => d.environments  ?? []))].sort();
  const hasChips = allTechs.length > 0 || allEnvs.length > 0;

  const visibleDocs = tagFilter
    ? documents.filter(d =>
        d.technologies?.some(t => t.toLowerCase() === tagFilter.toLowerCase()) ||
        d.environments?.some(e => e.toLowerCase() === tagFilter.toLowerCase()))
    : documents;

  function handleChipClick(tag: string) {
    setSearchParams(tagFilter?.toLowerCase() === tag.toLowerCase() ? {} : { tag });
  }

  return (
    <div className="dokumente-view">
      <div className="dokumente-header">
        <h2 className="dokumente-title">Dokumente</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            + Neues Dokument
          </button>
          <button className="header-icon-btn" title="Lerndokumentation"
            onClick={() => generateLerndokumentationPDF(currentUser, documents)}>
            <img src="/IconPDF.png" style={{ height: '22px', display: 'block' }} alt="Lerndokumentation" />
          </button>
        </div>
      </div>

      {hasChips && (
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 6, marginBottom: 14 }}>
          <button onClick={() => setSearchParams({})}
            style={{ borderRadius: 12, padding: '3px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer', border: '1.5px solid',
              background: !tagFilter ? '#1d4ed8' : 'transparent',
              color:      !tagFilter ? '#fff'    : 'var(--text-muted)',
              borderColor: !tagFilter ? '#1d4ed8' : '#d1d5db' }}>
            Alle
          </button>
          {allTechs.map(t => {
            const active = tagFilter?.toLowerCase() === t.toLowerCase();
            return (
              <button key={t} onClick={() => handleChipClick(t)}
                style={{ borderRadius: 12, padding: '3px 12px', fontSize: 12, fontWeight: 500, cursor: 'pointer', border: '1.5px solid',
                  background: active ? '#1e40af' : '#dbeafe',
                  color:      active ? '#fff'    : '#1e40af',
                  borderColor: active ? '#1e40af' : '#bfdbfe' }}>
                {t}
              </button>
            );
          })}
          {allEnvs.map(e => {
            const active = tagFilter?.toLowerCase() === e.toLowerCase();
            return (
              <button key={e} onClick={() => handleChipClick(e)}
                style={{ borderRadius: 12, padding: '3px 12px', fontSize: 12, fontWeight: 500, cursor: 'pointer', border: '1.5px solid',
                  background: active ? '#166534' : '#dcfce7',
                  color:      active ? '#fff'    : '#166534',
                  borderColor: active ? '#166534' : '#bbf7d0' }}>
                {e}
              </button>
            );
          })}
          {tagFilter && (
            <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 4 }}>
              {visibleDocs.length} Dokument{visibleDocs.length !== 1 ? 'e' : ''}
            </span>
          )}
        </div>
      )}

      {visibleDocs.length === 0 ? (
        <div className="no-user-state" style={{ marginTop: 60 }}>
          <p>{tagFilter ? `Keine Dokumente mit Tag «${tagFilter}».` : 'Noch keine Dokumente vorhanden.'}</p>
          {!tagFilter && <button className="btn btn-primary" onClick={() => setShowUpload(true)}>Erstes Dokument hochladen</button>}
        </div>
      ) : (
        <div className="doc-list">
          {visibleDocs.map(doc => (
            <DocRow key={doc.id} doc={doc} userId={currentUser.id}
              areas={areas} onDelete={handleDelete}
              isOpen={openDocId === doc.id}
              onToggle={() => setOpenDocId(prev => prev === doc.id ? null : doc.id)} />
          ))}
        </div>
      )}

      {showUpload && (
        <UploadModal
          userId={currentUser.id}
          activeApCode={activeAP?.code ?? currentUser.rotations[0]?.ap_code ?? null}
          onClose={() => setShowUpload(false)}
          onUploaded={doc => setOpenDocId(doc.id)}
        />
      )}
    </div>
  );
}
