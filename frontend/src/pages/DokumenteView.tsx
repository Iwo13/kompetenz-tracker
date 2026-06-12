import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useSearchParams } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { api } from '../api/client';
import type { UserDocument, BloomLevel, DocumentGoalLink } from '../types';

const BLOOM_LABELS = ['K0 – Keine', 'K1 – Wissen', 'K2 – Verstehen', 'K3 – Anwenden', 'K4 – Analysieren', 'K5 – Synthese', 'K6 – Beurteilen'];

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
  const [title,         setTitle]         = useState('');
  const [untertitel,    setUntertitel]    = useState('');
  const [apCode,        setApCode]        = useState(activeApCode ?? '');
  const [bewertungsart, setBewertungsart] = useState('manuell');
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
      fd.append('bewertungsart', bewertungsart);
      if (untertitel.trim()) fd.append('description', untertitel.trim());
      const doc = await uploadDocument(userId, fd);
      onUploaded(doc);
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
            <label className="upload-label">Ausbildungsplatz *</label>
            <select className="upload-input" value={apCode} onChange={e => setApCode(e.target.value)} required>
              <option value="">– Bitte wählen –</option>
              {availableAPs.map(ap => (
                <option key={ap.code} value={ap.code}>{ap.code} – {ap.name}</option>
              ))}
            </select>
          </div>
          <div className="upload-field">
            <label className="upload-label">Art der ersten Bewertung</label>
            <select className="upload-input" value={bewertungsart} onChange={e => setBewertungsart(e.target.value)}>
              <option value="manuell">Manuelle Bewertung</option>
              <option value="ai" disabled>Initialbewertung durch AI (demnächst)</option>
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
  const { updateDocumentGoal, updateDocument, reloadGoals, aiEvaluateDocument, currentUser, role } = useApp();
  const [showEdit,        setShowEdit]        = useState(false);
  const [saving,          setSaving]          = useState<string | null>(null);
  const [savingBewertung, setSavingBewertung] = useState(false);
  const [savedOk,         setSavedOk]         = useState(false);
  const [aiLoading,       setAiLoading]       = useState(false);
  const [aiError,         setAiError]         = useState<string | null>(null);
  const [localLinks, setLocalLinks] = useState(
    [...doc.goal_links].sort((a, b) => a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }))
  );

  // Textfelder mit Autosave
  const [kurzbeschreibung,       setKurzbeschreibung]       = useState(doc.kurzbeschreibung ?? '');
  const [umsetzung,              setUmsetzung]              = useState(doc.umsetzung ?? '');
  const [luecken,                setLuecken]                = useState(doc.luecken ?? '');
  const [feedbackBerufsbildner,  setFeedbackBerufsbildner]  = useState(doc.feedback_berufsbildner ?? '');
  const savingTextRef = useRef(false);

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
    const newEinschaetzung = field === 'einschaetzung' ? (value as string | null) : link.einschaetzung;
    const newBloom = field === 'bloom_level' ? (value as number | null) : link.bloom_level;
    setLocalLinks(prev => prev.map(l => l.goal_id === goalId
      ? { ...l, einschaetzung: newEinschaetzung, bloom_level: newBloom } : l));
    if (field === 'bloom_level' && newBloom !== -1) {
      setSaving(goalId);
      try { await updateDocumentGoal(userId, doc.id, goalId, newEinschaetzung, newBloom); }
      finally { setSaving(null); }
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
    try {
      const updated = await aiEvaluateDocument(currentUser.id, doc.id);
      setKurzbeschreibung(updated.kurzbeschreibung ?? '');
      setUmsetzung(updated.umsetzung ?? '');
      setLuecken(updated.luecken ?? '');
      setLocalLinks(
        [...updated.goal_links].sort((a, b) =>
          a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }))
      );
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
      const toRemove = localLinks.filter(l => l.bloom_level === -1);
      const toKeep   = localLinks.filter(l => l.bloom_level !== -1);

      // Leistungsziele entfernen (bloom = -1)
      if (toRemove.length > 0) {
        const remainingIds = toKeep.map(l => l.goal_id);
        await updateDocument(userId, doc.id, {
          title: doc.title,
          description: doc.description ?? undefined,
          ap_code: doc.ap_code,
          goal_ids: remainingIds,
          kurzbeschreibung: kurzbeschreibung || undefined,
          umsetzung:        umsetzung        || undefined,
          luecken:          luecken          || undefined,
        });
        setLocalLinks(toKeep);
      }

      // Effektive Kompetenzstufen aus DocumentGoalLinks neu berechnen
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
            <img src="/IconKommentiert.png" alt="Feedback vorhanden"
              style={{ width: 24, height: 24, objectFit: 'contain' }} />
          )}
          <span className="doc-ap-badge">{doc.ap_code}</span>
          <span className="doc-date">{formatDate(doc.uploaded_at)}</span>
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
              {doc.bewertungsart === 'ai' && (
                <button className="btn btn-secondary" style={{ fontSize: 13, borderColor: '#7c3aed', color: '#7c3aed' }}
                  onClick={handleAiEvaluate}
                  disabled={aiLoading}>
                  {aiLoading ? '⏳ AI analysiert…' : '✦ AI-Analyse starten'}
                </button>
              )}
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

            {/* Textfelder */}
            <div className="doc-text-fields">
              <div className="doc-text-field">
                <label className="doc-text-label">Kurzbeschreibung</label>
                <textarea className="doc-text-area" rows={3}
                  value={kurzbeschreibung}
                  onChange={e => setKurzbeschreibung(e.target.value)}
                  onBlur={() => saveTextFields({ kurzbeschreibung })}
                  placeholder="Beschreibung des Inhalts in 4/5 Sätzen. Was deckt es ab (Problemstellung, Funktion, Ergebnis)" />
              </div>
              <div className="doc-text-field">
                <label className="doc-text-label">Umsetzung der Arbeit</label>
                <textarea className="doc-text-area" rows={3}
                  value={umsetzung}
                  onChange={e => setUmsetzung(e.target.value)}
                  onBlur={() => saveTextFields({ umsetzung })}
                  placeholder="Wie wurde die Problemstellung gelöst, wie ist das Vorgehen und die Dokumentation." />
              </div>
              <div className="doc-text-field">
                <label className="doc-text-label">Lücken und Verbesserungsmöglichkeiten</label>
                <textarea className="doc-text-area" rows={3}
                  value={luecken}
                  onChange={e => setLuecken(e.target.value)}
                  onBlur={() => saveTextFields({ luecken })}
                  placeholder="Was könnte bei der nächsten Arbeit dieser Art berücksichtigt werden." />
              </div>
            </div>

            {/* Leistungsziel-Tabelle */}
            {localLinks.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 12 }}>
                Keine Leistungsziele verknüpft. Bitte «Leistungsziele zur Bewertung ändern» verwenden.
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
                      <tr key={link.goal_id}>
                        <td><strong>{link.goal_id.toUpperCase()}</strong></td>
                        <td style={{ fontSize: 12 }}>{gInfo?.text ?? link.goal_id}</td>
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
                              onChange={e => handleGoalUpdate(link.goal_id, 'bloom_level', Number(e.target.value))}
                              style={link.bloom_level === -1 ? { color: '#dc2626', fontStyle: 'italic' } : undefined}>
                              {([1,2,3,4,5,6] as BloomLevel[]).map(l => (
                                <option key={l} value={l}>{BLOOM_LABELS[l]}</option>
                              ))}
                              <option value={-1} style={{ color: '#dc2626' }}>— Leistungsziel entfernen</option>
                            </select>
                            {isSaving && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>…</span>}
                          </div>
                        </td>
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
  const [searchParams] = useSearchParams();
  const [showUpload, setShowUpload] = useState(false);
  const [openDocId,  setOpenDocId]  = useState<string | null>(null);

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

  return (
    <div className="dokumente-view">
      <div className="dokumente-header">
        <h2 className="dokumente-title">Dokumente</h2>
        <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
          + Neues Dokument
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="no-user-state" style={{ marginTop: 60 }}>
          <p>Noch keine Dokumente vorhanden.</p>
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            Erstes Dokument hochladen
          </button>
        </div>
      ) : (
        <div className="doc-list">
          {documents.map(doc => (
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
