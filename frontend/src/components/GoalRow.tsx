import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import type { Goal, BloomLevel } from '../types';

interface GoalRowProps {
  goal: Goal;
}

export default function GoalRow({ goal }: GoalRowProps) {
  const { currentUser, updateGoal } = useApp();
  const navigate = useNavigate();
  const userGoal = currentUser?.goals?.[goal.id];

  const manualLvl    = (userGoal?.manual_level ?? userGoal?.level ?? 0) as BloomLevel;
  const contributions = userGoal?.contributions ?? [];
  const docMaxLevel  = contributions.reduce((max, c) => Math.max(max, c.bloom_level), 0);

  const [level,   setLevel]   = useState<BloomLevel>(manualLvl);
  const [comment, setComment] = useState(userGoal?.comment ?? '');
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const effectiveLevel = Math.max(level, docMaxLevel) as BloomLevel;

  function handleLevel(l: BloomLevel) {
    const next = l === level ? 0 as BloomLevel : l;
    setLevel(next);
    updateGoal(goal.id, next, comment).catch(err => {
      console.error('Speichern fehlgeschlagen:', err);
      setLevel(level);
    });
  }

  function handleComment(val: string) {
    setComment(val);
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(
      () => updateGoal(goal.id, level, val).catch(console.error),
      600
    );
  }

  const date = userGoal?.date
    ? new Date(userGoal.date).toLocaleDateString('de-CH')
    : null;

  const allLevels = [0, 1, 2, 3, 4, 5, 6] as BloomLevel[];
  const maxReached = effectiveLevel >= goal.max;

  return (
    <div className="goal-row">
      <div className="goal-id">{goal.id.toUpperCase()}</div>
      <div className="goal-content">
        <div className="goal-text">{goal.text ?? goal.description}</div>
        <div className="goal-controls">
          <div className="k-buttons">
            {allLevels.map(l => (
              <button
                key={l}
                data-level={l}
                className={`k-btn${effectiveLevel === l ? ' selected' : ''}`}
                onClick={() => handleLevel(l)}
                title={`K${l}`}
              >
                K{l}
              </button>
            ))}
          </div>
          <span className={`goal-max-badge${maxReached ? ' goal-max-badge--reached' : ''}`}>
            Max: K{goal.max}
          </span>
        </div>
        {contributions.length > 0 && (
          <div className="goal-contributions">
            {contributions.map(c => (
              <span
                key={c.doc_id}
                className="goal-contrib-label"
                data-level={c.bloom_level}
                title={`${c.doc_title}: K${c.bloom_level} – Dokument öffnen`}
                onClick={() => navigate(`/dokumente?open=${c.doc_id}`)}
              >
                {c.doc_title}
              </span>
            ))}
          </div>
        )}
        {date && <div className="goal-date">Zuletzt gespeichert: {date}</div>}
        <textarea
          className="goal-comment"
          value={comment}
          onChange={e => handleComment(e.target.value)}
          placeholder="Kommentar / Notiz…"
          rows={2}
        />
      </div>
    </div>
  );
}
