import { SourceInfo, FieldPair } from '../types';

interface Props {
  source1: SourceInfo;
  source2: SourceInfo | null;
  sameSource: boolean;
  fieldPairs: FieldPair[];
  onFieldPairsChange: (pairs: FieldPair[]) => void;
  onBack: () => void;
  onContinue: () => void;
}

export default function FieldMapper({
  source1,
  source2,
  sameSource,
  fieldPairs,
  onFieldPairsChange,
  onBack,
  onContinue,
}: Props) {
  const effectiveSource2 = sameSource ? source1 : source2;

  const addPair = () => {
    onFieldPairsChange([...fieldPairs, { col1: '', col2: '' }]);
  };

  const removePair = (idx: number) => {
    onFieldPairsChange(fieldPairs.filter((_, i) => i !== idx));
  };

  const updatePair = (idx: number, key: 'col1' | 'col2', val: string) => {
    const next = fieldPairs.map((fp, i) => (i === idx ? { ...fp, [key]: val } : fp));
    onFieldPairsChange(next);
  };

  const canContinue = fieldPairs.some((fp) => fp.col1 !== '' && fp.col2 !== '');

  return (
    <div>
      <div className="section-header">STEP 3 — CONFIGURE FIELD MAPPING</div>
      <div className="field-mapper">
        <div className="field-mapper__header">
          <div className="field-mapper__header-cell">SOURCE 01 FIELD</div>
          <div className="field-mapper__header-cell" style={{ padding: '10px 0', textAlign: 'center' }}>=</div>
          <div className="field-mapper__header-cell">
            {sameSource ? 'SOURCE 01 FIELD (SELF)' : 'SOURCE 02 FIELD'}
          </div>
          <div className="field-mapper__header-cell" style={{ padding: '10px 0' }}></div>
        </div>

        <div className="field-mapper__rows">
          {fieldPairs.map((pair, idx) => (
            <div key={idx} className="field-mapper__row">
              <div className="field-mapper__cell">
                <div className="field-mapper__select-wrap">
                  <select
                    value={pair.col1}
                    onChange={(e) => updatePair(idx, 'col1', e.target.value)}
                  >
                    <option value="">— select field —</option>
                    {source1.columns.map((col) => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="field-mapper__eq">=</div>
              <div className="field-mapper__cell">
                <div className="field-mapper__select-wrap">
                  <select
                    value={pair.col2}
                    onChange={(e) => updatePair(idx, 'col2', e.target.value)}
                  >
                    <option value="">— select field —</option>
                    {(effectiveSource2 ? effectiveSource2.columns : source1.columns).map((col) => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="field-mapper__cell">
                {fieldPairs.length > 1 && (
                  <button
                    className="btn btn--small btn--danger"
                    onClick={() => removePair(idx)}
                    title="Remove"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="field-mapper__footer">
          <button className="btn btn--small" onClick={addPair}>+ ADD CONDITION</button>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn" onClick={onBack}>← BACK</button>
            <button className="btn btn--primary" onClick={onContinue} disabled={!canContinue}>
              CONTINUE →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
