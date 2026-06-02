export interface SourceInfo {
  sessionId: string;
  columns: string[];
  rowCount: number;
  fileName: string;
}

export interface FieldPair {
  col1: string;
  col2: string;
}

export interface MatchResult {
  id1_val: string;
  fields1_vals: Record<string, string>;
  id2_val: string;
  fields2_vals: Record<string, string>;
  match_score: number;
}

export type Step = 1 | 2 | 3 | 4 | 5;
