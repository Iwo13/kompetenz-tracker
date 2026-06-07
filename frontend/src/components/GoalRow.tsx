import { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';
import type { Goal, BloomLevel } from '../types';

interface GoalRowProps {
  goal: Goal;
}

export default function GoalRow({ goal }: GoalRowProps) {
  const { currentUser, updateGoal } = useApp();
  const userGoal = currentUser?.goals?.[goal.id] ?? { level: 0 as BloomLevel, comment: '' };

  const [level,   setLevel]   = useState<BloomLevel>(userGoal.level ?? 0);
  const [comment, setComment] = useState(userGoal.comment ?? '');
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  const date = userGoal.date
    ? new Date(userGoal.date).toLocaleDateString('de-CH')
    : null;

  const levels = ([0, 1, 2, 3, 4, 5, 6] as BloomLevel[]).slice(0, goal.max + 1);

  return (
    <div className="goal-row">
      <div className="goal-id">{goal.id.toUpperCase()}</div>
      <div className="goal-content">
        <div className="goal-text">{goal.text ?? goal.description}</div>
        <div className="goal-controls">
          <div className="k-buttons">
            {levels.map(l => (
              <button
                key={l}
                data-level={l}
                className={`k-btn${level === l ? ' selected' : ''}${l > goal.max ? ' over-max' : ''}`}
                onClick={() => handleLevel(l)}
                disabled={l > goal.max}
                title={`K${l}`}
              >
                K{l}
              </button>
            ))}
          </div>
          <span className="goal-max-badge">Max: K{goal.max}</span>
        </div>
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
