import { useState } from 'react';
import { SourceInfo, FieldPair, MatchResult } from '../types';
import { runMatch } from '../api';

interface Props {
  source1: SourceInfo;
  source2: SourceInfo | null;
  sameSource: boolean;
  idCol1: string;
  idCol2: string;
  fieldPairs: FieldPair[];
  isRunning: boolean;
  onRunningChange: (v: boolean) => void;
  onResults: (results: MatchResult[]) => void;
  onBack: () => void;
}

export default function RunEngine({
  source1,
  source2,
  sameSource,
  idCol1,
  idCol2,
  fieldPairs,
  isRunning,
  onRunningChange,
  onResults,
  onBack,
}: Props) {
  const [error, setError] = useState<string | null>(null);

  const effectiveSource2 = sameSource ? source1 : source2;
  const activePairs = fieldPairs.filter((fp) => fp.col1 && fp.col2);

  const handleExecute = async () => {
    if (!effectiveSource2) return;
    setError(null);
    onRunningChange(true);
    try {
      const res = await runMatch({
        sessionId1: source1.sessionId,
        sessionId2: effectiveSource2.sessionId,
        idCol1,
        idCol2: sameSource ? idCol2 : idCol2,
        fieldPairs: activePairs,
        sameSource,
      });
      onResults(res.results);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Matching failed');
      onRunningChange(false);
    }
  };

  return (
    <div>
      <div className="section-header">STEP 4 — EXECUTION</div>
      <div className="run-engine">
        <div className="run-engine__summary">
          <div className="run-engine__summary-title">CONFIGURATION SUMMARY</div>
          <div className="run-engine__summary-grid">
            <div className="run-engine__summary-block">
              <div className="run-engine__summary-label">SOURCE 01</div>
              <div className="run-engine__summary-value">{source1.fileName}</div>
              <div className="run-engine__summary-sub">
                {source1.rowCount.toLocaleString()} rows · ID: {idCol1}
              </div>
            </div>
            <div className="run-engine__summary-block">
              <div className="run-engine__summary-label">
                {sameSource ? 'SOURCE 02 (SELF-COMPARISON)' : 'SOURCE 02'}
              </div>
              <div className="run-engine__summary-value">
                {sameSource ? 'SELF' : effectiveSource2?.fileName || '—'}
              </div>
              <div className="run-engine__summary-sub">
                {sameSource
                  ? `${source1.rowCount.toLocaleString()} rows · ID: ${idCol2}`
                  : effectiveSource2
                  ? `${effectiveSource2.rowCount.toLocaleString()} rows · ID: ${idCol2}`
                  : '—'}
              </div>
            </div>
          </div>
          <div className="run-engine__rules">
            <div className="label" style={{ marginBottom: '8px' }}>MATCHING RULES ({activePairs.length})</div>
            {activePairs.map((fp, i) => (
              <div key={i} className="run-engine__rule">
                <span style={{ color: '#f0f0f0' }}>{fp.col1}</span>
                <span className="run-engine__rule-arrow"> ↔ </span>
                <span style={{ color: '#f0f0f0' }}>{fp.col2}</span>
                <span style={{ color: '#444444', fontSize: '10px' }}>(fuzzy)</span>
              </div>
            ))}
          </div>
        </div>

        <div className="run-engine__execute">
          {isRunning ? (
            <div className="run-engine__progress" style={{ width: '100%' }}>
              <div className="run-engine__progress-bar">
                <div className="run-engine__progress-fill" />
              </div>
              <div className="run-engine__progress-text">PROCESSING...</div>
            </div>
          ) : (
            <>
              {error && <div className="run-engine__error">{error}</div>}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn" onClick={onBack} disabled={isRunning}>← BACK</button>
                <button
                  className="btn btn--inverted"
                  onClick={handleExecute}
                  disabled={isRunning || activePairs.length === 0}
                  style={{ padding: '14px 32px', fontSize: '13px', letterSpacing: '0.12em' }}
                >
                  EXECUTE MATCHING ENGINE
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
