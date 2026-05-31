import { useState } from 'react';
import { useApp } from '../context/AppContext';
import type { User, Specialty } from '../types';

const SPECIALTIES: { value: Specialty; label: string }[] = [
  { value: 'app',           label: 'Applikations-\nentwicklung' },
  { value: 'platform',      label: 'Plattform-\nentwicklung' },
  { value: 'ict-fachmann',  label: 'ICT-Fachmann/\n-frau' },
];

interface UserModalProps {
  user?:    User;
  onClose:  () => void;
}

export default function UserModal({ user, onClose }: UserModalProps) {
  const { addUser, editUser, removeUser, selectUser } = useApp();
  const isEdit = !!user;

  const [name,      setName]      = useState(user?.name ?? '');
  const [specialty, setSpecialty] = useState<Specialty>(user?.specialty ?? 'app');
  const [startDate, setStartDate] = useState(user?.startDate?.slice(0, 10) ?? '');
  const [saving,    setSaving]    = useState(false);

  async function handleSave() {
    if (!name.trim() || !startDate) return;
    setSaving(true);
    try {
      if (isEdit && user) {
        await editUser(user.id, { name: name.trim(), specialty, start_date: startDate });
      } else {
        const created = await addUser({ name: name.trim(), specialty, start_date: startDate });
        selectUser(created.id);
      }
      onClose();
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

  return (
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
    </div>
  );
}
