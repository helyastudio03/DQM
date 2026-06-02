import { FieldPair, MatchResult } from './types';

const BASE_URL = 'http://localhost:8000';

export async function uploadFile(file: File): Promise<{ sessionId: string; columns: string[]; rowCount: number }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Upload failed');
  }

  const data = await res.json();
  return {
    sessionId: data.session_id,
    columns: data.columns,
    rowCount: data.row_count,
  };
}

export interface MatchParams {
  sessionId1: string;
  sessionId2: string;
  idCol1: string;
  idCol2: string;
  fieldPairs: FieldPair[];
  sameSource: boolean;
}

function buildMatchBody(params: MatchParams) {
  return {
    session_id_1: params.sessionId1,
    session_id_2: params.sessionId2,
    id_col_1: params.idCol1,
    id_col_2: params.idCol2,
    field_pairs: params.fieldPairs.map((fp) => ({ col1: fp.col1, col2: fp.col2 })),
    same_source: params.sameSource,
  };
}

export async function runMatch(params: MatchParams): Promise<{ results: MatchResult[]; totalCount: number }> {
  const res = await fetch(`${BASE_URL}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildMatchBody(params)),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Match failed');
  }

  const data = await res.json();
  return {
    results: data.results,
    totalCount: data.total_count,
  };
}

export async function exportResults(params: MatchParams): Promise<void> {
  const res = await fetch(`${BASE_URL}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildMatchBody(params)),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Export failed');
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'match_results.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${BASE_URL}/session/${sessionId}`, { method: 'DELETE' });
}
