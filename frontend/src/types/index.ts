// ── Domain-Typen gemäss Datenmodell (HK-App Konzept v4) ──────────────────────

export type Specialty = 'platform' | 'app' | 'ict-fachmann';

export type Role = 'berufsbildner' | 'lernender';

export type BloomLevel = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export interface GoalEntry {
  level:   BloomLevel;
  comment: string;
  date?:   string; // ISO 8601
}

export interface Rotation {
  id:      string;   // UUID
  von:     string;   // YYYY-MM-DD
  bis?:    string | null;
  ap_code: string;
}

export interface User {
  id:           string;   // UUID
  name:         string;
  specialty:    Specialty;
  start_date:   string;   // snake_case wie Backend liefert
  startDate:    string;   // camelCase Alias, im Context gesetzt
  email?:       string;
  external_id?: string;
  goals:        Record<string, GoalEntry>;
  rotations:    Rotation[];
}

export interface Goal {
  id:           string;
  text?:        string;        // UI-Anzeige (GoalRow)
  description?: string;        // PDF-Export
  max:          BloomLevel;
  specialty?:   Specialty | 'both';
}

export interface SubComp {
  id:    string;
  name:  string;
  goals: Goal[];
}

export interface Area {
  id:        string;
  name:      string;
  color?:    string;
  specialty?: Specialty | 'both';
  subComps:  SubComp[];
}

export interface AusbildungsplatzHkCoverage {
  [bildungsplan: string]: Record<string, string>;
}

export interface Ausbildungsplatz {
  code:         string;
  name:         string;
  abLehrjahr?:  number;
  bereiche?:    Record<string, string | null>;
  hk_coverage?: AusbildungsplatzHkCoverage;
}

// ── Hilfstypen ──────────────────────────────────────────────────────────────

export interface ProgressInfo {
  reached: number;
  max:     number;
  pct:     number;
}

export interface LehrjahrInfo {
  current:  number;
  total:    number;
  monthsIn: number;
}
