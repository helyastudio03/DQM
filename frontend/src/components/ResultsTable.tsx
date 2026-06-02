import { useState, useMemo } from 'react';
import { MatchResult, SourceInfo, FieldPair } from '../types';
import { exportResults } from '../api';

interface Props {
  results: MatchResult[];
  source1: SourceInfo;
  source2: SourceInfo | null;
  sameSource: boolean;
  idCol1: string;
  idCol2: string;
  fieldPairs: FieldPair[];
  onNewAnalysis: () => void;
}

type SortKey = 'id1_val' | 'id2_val' | 'match_score';
type SortDir = 'asc' | 'desc';

export default function ResultsTable({
  results,
  source1,
  source2,
  sameSource,
  idCol1,
  idCol2,
  fieldPairs,
  onNewAnalysis,
}: Props) {
  const [minScore, setMinScore] = useState(50);
  const [sortKey, setSortKey] = useState<SortKey>('match_score');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [exporting, setExporting] = useState(false);

  const effectiveSource2 = sameSource ? source1 : source2;

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir(key === 'match_score' ? 'desc' : 'asc');
    }
  };

  const filtered = useMemo(() => {
    return results
      .filter((r) => r.match_score >= minScore)
      .sort((a, b) => {
        let av: string | number = a[sortKey];
        let bv: string | number = b[sortKey];
        if (sortKey === 'match_score') {
          av = a.match_score;
          bv = b.match_score;
          return sortDir === 'asc' ? (av as number) - (bv as number) : (bv as number) - (av as number);
        }
        return sortDir === 'asc'
          ? String(av).localeCompare(String(bv))
          : String(bv).localeCompare(String(av));
      });
  }, [results, minScore, sortKey, sortDir]);

  const handleExport = async () => {
    if (!effectiveSource2) return;
    setExporting(true);
    try {
      await exportResults({
        sessionId1: source1.sessionId,
        sessionId2: effectiveSource2.sessionId,
        idCol1,
        idCol2,
        fieldPairs: fieldPairs.filter((fp) => fp.col1 && fp.col2),
        sameSource,
      });
    } catch (e) {
      console.error('Export failed', e);
    } finally {
      setExporting(false);
    }
  };

  const formatFields = (fields: Record<string, string>) => {
    return Object.entries(fields)
      .map(([k, v]) => `${k}:${v}`)
      .join(', ');
  };

  const SortIcon = ({ col }: { col: SortKey }) => (
    <span className={'results__sort-icon' + (sortKey === col ? ' results__sort-icon--active' : '')}>
      {sortKey === col ? (sortDir === 'asc' ? '↑' : '↓') : '↕'}
    </span>
  );

  return (
    <div className="results">
      <div className="results__header">
        <div className="results__title">
          MATCH RESULTS — {filtered.length} PAIRS IDENTIFIED
        </div>
        <div className="results__actions">
          <button
            className="btn btn--small"
            onClick={handleExport}
            disabled={exporting || filtered.length === 0}
          >
            {exporting ? 'EXPORTING...' : 'EXPORT CSV'}
          </button>
          <button className="btn btn--small btn--primary" onClick={onNewAnalysis}>
            ← NEW ANALYSIS
          </button>
        </div>
      </div>

      <div className="results__controls">
        <span className="results__filter-label">MINIMUM SCORE</span>
        <input
          type="range"
          min={0}
          max={100}
          value={minScore}
          onChange={(e) => setMinScore(Number(e.target.value))}
          className="results__filter-range"
        />
        <span className="results__score-val">{minScore}%</span>
        <span style={{ fontSize: '11px', color: '#444444' }}>
          {filtered.length} / {results.length} pairs shown
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="results__empty">NO PAIRS MATCH THE CURRENT FILTER</div>
      ) : (
        <div className="results__table-wrap">
          <table className="results__table">
            <thead>
              <tr>
                <th onClick={() => handleSort('id1_val')}>
                  ID (SOURCE 01) <SortIcon col="id1_val" />
                </th>
                <th>FIELDS (SOURCE 01)</th>
                <th onClick={() => handleSort('match_score')}>
                  SCORE <SortIcon col="match_score" />
                </th>
                <th onClick={() => handleSort('id2_val')}>
                  ID ({sameSource ? 'SOURCE 01 SELF' : 'SOURCE 02'}) <SortIcon col="id2_val" />
                </th>
                <th>FIELDS ({sameSource ? 'SOURCE 01 SELF' : 'SOURCE 02'})</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i}>
                  <td className="results__id-cell">{r.id1_val}</td>
                  <td className="results__fields-cell">{formatFields(r.fields1_vals)}</td>
                  <td className="results__score-cell">
                    <div className="results__score-bar-wrap">
                      <div
                        className="results__score-bar-fill"
                        style={{ width: `${r.match_score}%` }}
                      />
                      <span className="results__score-text">{r.match_score.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="results__id-cell">{r.id2_val}</td>
                  <td className="results__fields-cell">{formatFields(r.fields2_vals)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
