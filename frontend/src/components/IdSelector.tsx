import { SourceInfo } from '../types';

interface Props {
  source1: SourceInfo;
  source2: SourceInfo | null;
  sameSource: boolean;
  idCol1: string;
  idCol2: string;
  onIdCol1Change: (v: string) => void;
  onIdCol2Change: (v: string) => void;
  onBack: () => void;
  onContinue: () => void;
}

export default function IdSelector({
  source1,
  source2,
  sameSource,
  idCol1,
  idCol2,
  onIdCol1Change,
  onIdCol2Change,
  onBack,
  onContinue,
}: Props) {
  const canContinue = idCol1 !== '' && (sameSource || idCol2 !== '');

  const effectiveSource2 = sameSource ? source1 : source2;

  return (
    <div>
      <div className="section-header">STEP 2 — SELECT TECHNICAL IDENTIFIERS</div>
      <div className="id-selector">
        <div className="id-selector__panel">
          <div className="id-selector__title">TECHNICAL IDENTIFIER — SOURCE 01</div>
          <div className="id-selector__source-name">{source1.fileName}</div>
          <div className="label" style={{ marginBottom: '6px' }}>SELECT ID COLUMN</div>
          <div className="id-selector__select-wrap">
            <select
              value={idCol1}
              onChange={(e) => onIdCol1Change(e.target.value)}
            >
              <option value="">— select column —</option>
              {source1.columns.map((col) => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>
          {idCol1 && (
            <div style={{ marginTop: '8px', fontSize: '11px', color: '#888888' }}>
              Selected: <span style={{ color: '#f0f0f0' }}>{idCol1}</span>
            </div>
          )}
        </div>

        <div className="id-selector__panel">
          <div className="id-selector__title">
            TECHNICAL IDENTIFIER — {sameSource ? 'SOURCE 01 (SELF)' : 'SOURCE 02'}
          </div>
          <div className="id-selector__source-name">
            {effectiveSource2 ? effectiveSource2.fileName : '—'}
            {sameSource && <span style={{ fontSize: '10px', color: '#888888', marginLeft: '8px' }}>[SELF-COMPARISON]</span>}
          </div>
          {!sameSource && effectiveSource2 ? (
            <>
              <div className="label" style={{ marginBottom: '6px' }}>SELECT ID COLUMN</div>
              <div className="id-selector__select-wrap">
                <select
                  value={idCol2}
                  onChange={(e) => onIdCol2Change(e.target.value)}
                >
                  <option value="">— select column —</option>
                  {effectiveSource2.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              {idCol2 && (
                <div style={{ marginTop: '8px', fontSize: '11px', color: '#888888' }}>
                  Selected: <span style={{ color: '#f0f0f0' }}>{idCol2}</span>
                </div>
              )}
            </>
          ) : sameSource ? (
            <>
              <div className="label" style={{ marginBottom: '6px' }}>SELECT ID COLUMN</div>
              <div className="id-selector__select-wrap">
                <select
                  value={idCol2}
                  onChange={(e) => onIdCol2Change(e.target.value)}
                >
                  <option value="">— select column —</option>
                  {source1.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              {idCol2 && (
                <div style={{ marginTop: '8px', fontSize: '11px', color: '#888888' }}>
                  Selected: <span style={{ color: '#f0f0f0' }}>{idCol2}</span>
                </div>
              )}
            </>
          ) : null}
        </div>

        <div className="id-selector__footer">
          <button className="btn" onClick={onBack} style={{ marginRight: '8px' }}>← BACK</button>
          <button className="btn btn--primary" onClick={onContinue} disabled={!canContinue}>
            CONTINUE →
          </button>
        </div>
      </div>
    </div>
  );
}
