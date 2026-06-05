import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useApp } from '../context/AppContext';

interface APModalProps {
  onClose: () => void;
}

export default function APModal({ onClose }: APModalProps) {
  const { addAusbildungsplatz } = useApp();
  const [code,       setCode]      = useState('');
  const [name,       setName]      = useState('');
  const [abLehrjahr, setAbLj]      = useState(2);
  const [saving,     setSaving]    = useState(false);
  const [error,      setError]     = useState('');

  async function handleSave() {
    if (!code.trim() || !name.trim()) return;
    setSaving(true);
    setError('');
    try {
      await addAusbildungsplatz({ code: code.trim().toUpperCase(), name: name.trim(), abLehrjahr });
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  }

  return createPortal(
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Ausbildungsplatz erfassen</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label className="form-label">Kürzel (z.B. SWE, SA, COL)</label>
            <input className="form-input" value={code} onChange={e => setCode(e.target.value)}
              placeholder="Kürzel" maxLength={10} />
          </div>
          <div className="form-group">
            <label className="form-label">Bezeichnung</label>
            <input className="form-input" value={name} onChange={e => setName(e.target.value)}
              placeholder="z.B. Software Engineering" />
          </div>
          <div className="form-group">
            <label className="form-label">Ab Lehrjahr</label>
            <select className="form-input" value={abLehrjahr}
              onChange={e => setAbLj(Number(e.target.value))}>
              <option value={1}>1. Lehrjahr (Basislehrjahr)</option>
              <option value={2}>2. Lehrjahr</option>
            </select>
          </div>
          {error && <div className="form-error">{error}</div>}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Abbrechen</button>
          <button className="btn btn-primary" onClick={handleSave}
            disabled={saving || !code.trim() || !name.trim()}>
            {saving ? 'Speichern…' : 'Speichern'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
