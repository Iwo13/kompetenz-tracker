import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import type { Goal, BloomLevel } from '../types';

interface GoalRowProps {
  goal: Goal;
}

interface AiSuggestion {
  bloom_level: number;
  begruendung: string;
  optimierter_text: string | null;
}

export default function GoalRow({ goal }: GoalRowProps) {
  const { currentUser, updateGoal, aiSuggestGoal } = useApp();
  const navigate = useNavigate();
  const userGoal = currentUser?.goals?.[goal.id];

  const manualLvl    = (userGoal?.manual_level ?? userGoal?.level ?? 0) as BloomLevel;
  const contributions = userGoal?.contributions ?? [];
  const docMaxLevel  = contributions.reduce((max, c) => Math.max(max, c.bloom_level), 0);

  const [level,   setLevel]   = useState<BloomLevel>(manualLvl);
  const [comment, setComment] = useState(userGoal?.comment ?? '');
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [aiLoading,    setAiLoading]    = useState(false);
  const [aiError,      setAiError]      = useState<string | null>(null);
  const [aiSuggestion, setAiSuggestion] = useState<AiSuggestion | null>(null);

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

  async function handleAiSuggest() {
    if (!comment.trim()) return;
    setAiLoading(true);
    setAiError(null);
    setAiSuggestion(null);
    try {
      const res = await aiSuggestGoal(goal.id, comment);
      setAiSuggestion({
        bloom_level:      res.bloom_level,
        begruendung:      res.begruendung,
        optimierter_text: res.optimierter_text,
      });
    } catch {
      setAiError('KI-Vorschlag fehlgeschlagen. Bitte Konfiguration prüfen.');
    } finally {
      setAiLoading(false);
    }
  }

  function applySuggestedLevel(l: BloomLevel) {
    setLevel(l);
    updateGoal(goal.id, l, comment).catch(err => {
      console.error('Speichern fehlgeschlagen:', err);
      setLevel(level);
    });
    setAiSuggestion(null);
  }

  function applyOptimizedText(text: string) {
    setComment(text);
    updateGoal(goal.id, level, text).catch(console.error);
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
        <div className="goal-ai-row">
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: 12, borderColor: '#7c3aed', color: '#7c3aed' }}
            onClick={handleAiSuggest}
            disabled={aiLoading || !comment.trim()}
            title="KI schlägt anhand des Kommentars eine Bloom-Stufe vor"
          >
            {aiLoading ? <><span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>{' '}KI analysiert…</> : '✦ KI-Vorschlag'}
          </button>
        </div>
        {aiError && <p style={{ color: '#dc2626', fontSize: 12, margin: '4px 0 0' }}>{aiError}</p>}
        {aiSuggestion && (
          <div className="goal-ai-suggestion">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="k-btn" data-level={aiSuggestion.bloom_level} style={{ cursor: 'default' }}>
                K{aiSuggestion.bloom_level}
              </span>
              <span style={{ fontSize: 12.5, flex: 1 }}>{aiSuggestion.begruendung}</span>
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
              <button type="button" className="btn btn-primary" style={{ fontSize: 12 }}
                onClick={() => applySuggestedLevel(aiSuggestion.bloom_level as BloomLevel)}>
                Vorschlag übernehmen
              </button>
              <button type="button" className="btn btn-secondary" style={{ fontSize: 12 }}
                onClick={() => setAiSuggestion(null)}>
                Verwerfen
              </button>
            </div>
            {aiSuggestion.optimierter_text && (
              <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px dashed var(--border)' }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4 }}>
                  Formulierungsvorschlag
                </div>
                <p style={{ fontSize: 12.5, margin: '0 0 6px', whiteSpace: 'pre-wrap' }}>{aiSuggestion.optimierter_text}</p>
                <button type="button" className="btn btn-secondary" style={{ fontSize: 12 }}
                  onClick={() => applyOptimizedText(aiSuggestion.optimierter_text as string)}>
                  Text übernehmen
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
