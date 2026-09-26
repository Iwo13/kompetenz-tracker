import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useApp } from '../context/AppContext';
import type { User, Specialty } from '../types';

const SPECIALTIES: { value: Specialty; label: string }[] = [
  { value: 'app',               label: 'Applikations-\nentwicklung' },
  { value: 'platform',          label: 'Plattform-\nentwicklung' },
  { value: 'ict-fachmann',      label: 'ICT-Fachmann/\n-frau' },
  { value: 'betriebsinformatik', label: 'Betriebs-\ninformatik' },
];

interface UserModalProps {
  user?:    User;
  onClose:  () => void;
}

export default function UserModal({ user, onClose }: UserModalProps) {
  const { addUser, editUser, removeUser, selectUser } = useApp();
  const isEdit = !!user;

  const [name,      setName]      = useState(user?.name ?? '');
  const [email,     setEmail]     = useState(user?.email ?? '');
  const [specialty, setSpecialty] = useState<Specialty>(user?.specialty ?? 'app');
  const [startDate, setStartDate] = useState(user?.startDate?.slice(0, 10) ?? '');
  const [saving,    setSaving]    = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  async function handleSave() {
    if (!name.trim() || !startDate) return;
    setSaving(true);
    setSaveError(null);
    try {
      if (isEdit && user) {
        await editUser(user.id, { name: name.trim(), specialty, start_date: startDate, email: email.trim() || undefined });
      } else {
        const created = await addUser({ name: name.trim(), specialty, start_date: startDate, email: email.trim() || undefined });
        selectUser(created.id);
      }
      onClose();
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Unbekannter Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!user) return;
    if (!window.confirm(`${user.name} wirklich löschen?`)) return;
    await removeUser(user.id);
    onClose();
  }

  return createPortal(
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>{isEdit ? 'Lernende/n bearbeiten' : 'Lernende/n erfassen'}</h2>

        <div className="form-group">
          <label>Name</label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Vorname Nachname"
            autoFocus
          />
        </div>

        <div className="form-group">
          <label>E-Mail-Adresse</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="vorname.nachname@fhnw.ch"
          />
        </div>

        <div className="form-group">
          <label>Ausbildung</label>
          <div className="specialty-cards-modal">
            {SPECIALTIES.map(s => (
              <button
                key={s.value}
                className={`specialty-card-btn${specialty === s.value ? ' selected' : ''}`}
                onClick={() => setSpecialty(s.value)}
                style={{ whiteSpace: 'pre-line' }}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Lehrbeginn</label>
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
          />
        </div>

        {saveError && (
          <div style={{ color: '#dc2626', fontSize: '0.85rem', marginBottom: '0.5rem', padding: '0.5rem', background: '#fee2e2', borderRadius: '4px' }}>
            Fehler: {saveError}
          </div>
        )}

        <div className="modal-actions">
          {isEdit && (
            <button className="btn btn-danger" onClick={handleDelete}>Löschen</button>
          )}
          <button className="btn btn-secondary" onClick={onClose}>Abbrechen</button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={saving || !name.trim() || !startDate}
          >
            {saving ? 'Speichern…' : 'Speichern'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
