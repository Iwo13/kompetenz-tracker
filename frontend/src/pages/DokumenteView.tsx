import { useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useApp } from '../context/AppContext';
import type { UserDocument, BloomLevel } from '../types';

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
  areas: import('../types').Area[];
  onClose: () => void;
  onUploaded: (doc: UserDocument) => void;
}

function UploadModal({ userId, activeApCode, areas, onClose, onUploaded }: UploadModalProps) {
  const { uploadDocument, ausbildungsplaetze, currentUser } = useApp();
  const fileRef = useRef<HTMLInputElement>(null);
  const [title,         setTitle]         = useState('');
  const [description,   setDescription]   = useState('');
  const [apCode,        setApCode]        = useState(activeApCode ?? '');
  const [selectedGoals, setSelectedGoals] = useState<Set<string>>(new Set());
  const [openAreas,     setOpenAreas]     = useState<Set<string>>(new Set());
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

  function toggleGoal(id: string) {
    setSelectedGoals(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }

  function toggleArea(areaId: string) {
    setOpenAreas(prev => { const n = new Set(prev); n.has(areaId) ? n.delete(areaId) : n.add(areaId); return n; });
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!file)   { setError('Bitte eine Datei wählen.'); return; }
    if (!apCode) { setError('Bitte einen Ausbildungsplatz wählen.'); return; }
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('title', title.trim() || file.name);
      fd.append('apCode', apCode);
      if (description.trim()) fd.append('description', description.trim());
      if (selectedGoals.size > 0) fd.append('goalIds', [...selectedGoals].join(','));
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

        {/* Header */}
        <div className="upload-modal-header">
          <h2 className="upload-modal-title">Neues Dokument</h2>
          <button className="upload-modal-close" onClick={onClose} type="button">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="upload-modal-form">
          {/* Datei */}
          <div className="upload-field">
            <label className="upload-label">Datei *</label>
            <input ref={fileRef} type="file" onChange={handleFileChange} className="upload-file-input" />
          </div>

          {/* Titel */}
          <div className="upload-field">
            <label className="upload-label">Titel *</label>
            <input className="upload-input" value={title} onChange={e => setTitle(e.target.value)}
              placeholder="Titel des Dokuments" required />
          </div>

          {/* Beschreibung */}
          <div className="upload-field">
            <label className="upload-label">Beschreibung</label>
            <textarea className="upload-input" rows={2} value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Kurze Beschreibung (optional)" />
          </div>

          {/* Ausbildungsplatz */}
          <div className="upload-field">
            <label className="upload-label">Ausbildungsplatz *</label>
            <select className="upload-input" value={apCode} onChange={e => setApCode(e.target.value)} required>
              <option value="">– Bitte wählen –</option>
              {availableAPs.map(ap => (
                <option key={ap.code} value={ap.code}>{ap.code} – {ap.name}</option>
              ))}
            </select>
          </div>

          {/* HK-Auswahl gruppiert nach Bereichen */}
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
                    <button type="button" className="upload-hk-area-header"
                      onClick={() => toggleArea(area.id)}>
                      <span className="upload-hk-area-toggle">{isOpen ? '▼' : '▶'}</span>
                      <span className="upload-hk-area-name">{area.id.toUpperCase()} – {area.name}</span>
                      {selectedInArea > 0 && (
                        <span className="upload-hk-badge">{selectedInArea}</span>
                      )}
                    </button>
                    {isOpen && (
                      <div className="upload-hk-goals">
                        {areaGoals.map(g => (
                          <label key={g.id} className="upload-hk-goal">
                            <input type="checkbox" checked={selectedGoals.has(g.id)}
                              onChange={() => toggleGoal(g.id)} />
                            <span><strong>{g.id}</strong> – {g.text ?? g.id}</span>
                          </label>
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
              {saving ? 'Wird hochgeladen…' : 'Hochladen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

// ── Edit Document Modal ────────────────────────────────────────────────────────
interface EditDocModalProps {
  doc: UserDocument;
  userId: string;
  areas: import('../types').Area[];
  onClose: () => void;
}

function EditDocModal({ doc, userId, areas, onClose }: EditDocModalProps) {
  const { updateDocument, ausbildungsplaetze, currentUser } = useApp();
  const [title,         setTitle]         = useState(doc.title);
  const [description,   setDescription]   = useState(doc.description ?? '');
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

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    try {
      await updateDocument(userId, doc.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        ap_code: apCode,
        goal_ids: [...selectedGoals],
      });
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
          <h2 className="upload-modal-title">Dokumentinformationen anpassen</h2>
          <button className="upload-modal-close" onClick={onClose} type="button">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="upload-modal-form">
          <div className="upload-field">
            <label className="upload-label">Datei</label>
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              {doc.file_name} · {(doc.file_size / 1024).toFixed(0)} KB
            </span>
          </div>
          <div className="upload-field">
            <label className="upload-label">Titel *</label>
            <input className="upload-input" value={title} onChange={e => setTitle(e.target.value)} required />
          </div>
          <div className="upload-field">
            <label className="upload-label">Beschreibung</label>
            <textarea className="upload-input" rows={2} value={description}
              onChange={e => setDescription(e.target.value)} placeholder="Kurze Beschreibung (optional)" />
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
                        {areaGoals.map(g => (
                          <label key={g.id} className="upload-hk-goal">
                            <input type="checkbox" checked={selectedGoals.has(g.id)} onChange={() => toggleGoal(g.id)} />
                            <span><strong>{g.id}</strong> – {g.text ?? g.id}</span>
                          </label>
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
  const { updateDocumentGoal, currentUser } = useApp();
  const [showEdit, setShowEdit] = useState(false);
  const [saving,   setSaving]   = useState<string | null>(null);
  const [localLinks, setLocalLinks] = useState(
    [...doc.goal_links].sort((a, b) => a.goal_id.localeCompare(b.goal_id, undefined, { numeric: true }))
  );

  const areaBadges = [...new Set(doc.goal_links.map(l => l.goal_id[0].toUpperCase()))].sort();

  const goalMap = new Map(areas.flatMap(a => a.subComps.flatMap(sc =>
    sc.goals.map(g => [g.id, { text: g.text ?? g.id, max: g.max }])
  )));

  async function handleGoalUpdate(goalId: string, field: 'einschaetzung' | 'bloom_level', value: string | number | null) {
    const link = localLinks.find(l => l.goal_id === goalId);
    if (!link) return;
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

  async function handleEinschaetzungBlur(goalId: string) {
    const link = localLinks.find(l => l.goal_id === goalId);
    if (!link) return;
    setSaving(goalId);
    try { await updateDocumentGoal(userId, doc.id, goalId, link.einschaetzung, link.bloom_level); }
    finally { setSaving(null); }
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
          <span className="doc-ap-badge">{doc.ap_code}</span>
          <span className="doc-date">{formatDate(doc.uploaded_at)}</span>
          <span className="accordion-icon">{open ? '×' : '+'}</span>
        </button>

        {/* Body */}
        {open && (
          <div className="doc-row-body">
            <div style={{ display: 'flex', gap: 10, marginBottom: 14, alignItems: 'center' }}>
              <a href={`http://localhost:5000/users/${userId}/documents/${doc.id}/file`}
                target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ fontSize: 13 }}>
                ⬇ Datei öffnen
              </a>
              <button className="btn btn-secondary" style={{ fontSize: 13 }}
                onClick={() => setShowEdit(true)}>
                ✎ Anpassen
              </button>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', flex: 1 }}>
                {doc.file_name} · {(doc.file_size / 1024).toFixed(0)} KB · AP: <strong>{doc.ap_code}</strong> · {formatDate(doc.uploaded_at)}
              </span>
              <button className="btn btn-secondary" style={{ fontSize: 12, color: '#dc2626', borderColor: '#dc2626' }}
                onClick={() => onDelete(doc.id)}>
                🗑 Löschen
              </button>
            </div>

            {localLinks.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Keine Handlungskompetenzen verknüpft.</p>
            ) : (
              <table className="doc-goal-table">
                <thead>
                  <tr>
                    <th>Kompetenz</th>
                    <th>Beschreibung</th>
                    <th>Einschätzung</th>
                    <th>Bloom-Stufe (aktuell)</th>
                    <th>Anpassung</th>
                  </tr>
                </thead>
                <tbody>
                  {localLinks.map(link => {
                    const gInfo = goalMap.get(link.goal_id);
                    const currentLevel = currentUser?.goals[link.goal_id]?.level ?? 0;
                    const isSaving = saving === link.goal_id;
                    return (
                      <tr key={link.goal_id}>
                        <td><strong>{link.goal_id}</strong></td>
                        <td style={{ fontSize: 12 }}>{gInfo?.text ?? link.goal_id}</td>
                        <td>
                          <textarea className="doc-einschaetzung" rows={2}
                            value={link.einschaetzung ?? ''}
                            onChange={e => handleGoalUpdate(link.goal_id, 'einschaetzung', e.target.value)}
                            onBlur={() => handleEinschaetzungBlur(link.goal_id)}
                            placeholder="Einschätzung…" />
                        </td>
                        <td style={{ fontSize: 13, whiteSpace: 'nowrap' }}>K{currentLevel}</td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <select className="doc-bloom-select" disabled={isSaving}
                              value={link.bloom_level ?? currentLevel}
                              onChange={e => handleGoalUpdate(link.goal_id, 'bloom_level', Number(e.target.value))}>
                              {([1,2,3,4,5,6] as BloomLevel[]).map(l => (
                                <option key={l} value={l}>{BLOOM_LABELS[l]}</option>
                              ))}
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
        <EditDocModal doc={doc} userId={userId} areas={areas} onClose={() => setShowEdit(false)} />
      )}
    </>
  );
}

// ── Haupt-View ─────────────────────────────────────────────────────────────────
export default function DokumenteView() {
  const { currentUser, documents, deleteDocument, areas, activeAP } = useApp();
  const [showUpload, setShowUpload] = useState(false);
  const [openDocId,  setOpenDocId]  = useState<string | null>(null);

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
          areas={areas}
          onClose={() => setShowUpload(false)}
          onUploaded={() => {}}
        />
      )}
    </div>
  );
}
