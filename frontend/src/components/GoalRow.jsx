import { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';

export default function GoalRow({ goal }) {
  const { currentUser, updateGoal } = useApp();
  const userGoal = currentUser?.goals?.[goal.id] ?? { level: 0, comment: '' };

  const [level,   setLevel]   = useState(userGoal.level ?? 0);
  const [comment, setComment] = useState(userGoal.comment ?? '');
  const saveTimer = useRef(null);

  function handleLevel(l) {
    const next = l === level ? 0 : l;
    setLevel(next);
    updateGoal(goal.id, next, comment);
  }

  function handleComment(val) {
    setComment(val);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => updateGoal(goal.id, level, val), 600);
  }

  const date = userGoal.date
    ? new Date(userGoal.date).toLocaleDateString('de-CH')
    : null;

  return (
    <div className="goal-row">
      <div className="goal-id">{goal.id}</div>
      <div className="goal-content">
        <div className="goal-text">{goal.text}</div>
        <div className="goal-controls">
          <div className="k-buttons">
            {[0, 1, 2, 3, 4, 5, 6].slice(0, goal.max + 1).map(l => (
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
