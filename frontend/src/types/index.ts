// ── Domain-Typen gemäss Datenmodell (HK-App Konzept v4) ──────────────────────

export type Specialty = 'platform' | 'app' | 'ict-fachmann' | 'betriebsinformatik';

export type Role = 'berufsbildner' | 'lernender';

export type BloomLevel = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export interface GoalContribution {
  doc_id:      string;
  doc_title:   string;
  bloom_level: number;
}

export interface GoalEntry {
  level:          BloomLevel; // effective = max(manual, doc contributions)
  manual_level?:  BloomLevel; // direct user assessment only
  comment:        string;
  date?:          string; // ISO 8601
  contributions?: GoalContribution[];
}

export interface Rotation {
  id:      string;   // UUID
  von:     string;   // YYYY-MM-DD
  bis?:    string | null;
  ap_code: string;
}

export interface DocumentGoalLink {
  id:            string;
  goal_id:       string;
  einschaetzung: string | null;
  bloom_level:   number | null;
}

export interface UserDocument {
  id:               string;
  user_id:          string;
  ap_code:          string;
  title:            string;
  description:      string | null;
  kurzbeschreibung: string | null;
  umsetzung:        string | null;
  luecken:          string | null;
  bewertungsart:             string;
  feedback_berufsbildner:    string | null;
  technologies:              string[];
  environments:              string[];
  document_date:             string | null;
  file_name:                 string;
  content_type:     string;
  file_size:        number;
  uploaded_at:      string;
  goal_links:       DocumentGoalLink[];
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
  achieved: number;
  total:    number;
  pct:      number;
}

export interface LehrjahrInfo {
  current:  number;
  total:    number;
  monthsIn: number;
}
