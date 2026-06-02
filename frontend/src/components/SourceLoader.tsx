import { useRef, useState, DragEvent } from 'react';
import { SourceInfo } from '../types';
import { uploadFile } from '../api';

interface Props {
  source1: SourceInfo | null;
  source2: SourceInfo | null;
  sameSource: boolean;
  onSource1Change: (s: SourceInfo | null) => void;
  onSource2Change: (s: SourceInfo | null) => void;
  onSameSourceChange: (val: boolean) => void;
  onContinue: () => void;
}

function UploadPanel({
  title,
  source,
  onSourceChange,
  disabled,
}: {
  title: string;
  source: SourceInfo | null;
  onSourceChange: (s: SourceInfo | null) => void;
  disabled?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setLoading(true);
    try {
      const result = await uploadFile(file);
      onSourceChange({
        sessionId: result.sessionId,
        columns: result.columns,
        rowCount: result.rowCount,
        fileName: file.name,
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const onDragLeave = () => setDragging(false);

  return (
    <div className={'source-panel' + (disabled ? ' source-panel--disabled' : '')}>
      <div className="source-panel__title">{title}</div>

      {!source ? (
        <>
          <div
            className={'source-panel__dropzone' + (dragging ? ' source-panel__dropzone--active' : '')}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={() => inputRef.current?.click()}
          >
            <div className="source-panel__dropzone-text">
              {loading ? 'UPLOADING...' : 'DROP FILE HERE OR CLICK TO BROWSE'}
            </div>
            <div className="source-panel__dropzone-sub">.CSV · .XLSX · .PARQUET</div>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx,.parquet"
            style={{ display: 'none' }}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.target.value = '';
            }}
          />
          {error && <div style={{ color: '#ff4444', fontSize: '11px' }}>{error}</div>}
        </>
      ) : (
        <div className="source-panel__info">
          <div className="source-panel__filename">{source.fileName}</div>
          <div className="source-panel__meta">
            {source.rowCount.toLocaleString()} ROWS · {source.columns.length} COLUMNS
          </div>
          <div className="source-panel__columns">
            {source.columns.map((col) => (
              <span key={col} className="source-panel__col-tag">{col}</span>
            ))}
          </div>
          <button
            className="btn btn--small"
            onClick={() => onSourceChange(null)}
            style={{ marginTop: '8px', alignSelf: 'flex-start' }}
          >
            REMOVE
          </button>
        </div>
      )}
    </div>
  );
}

export default function SourceLoader({
  source1,
  source2,
  sameSource,
  onSource1Change,
  onSource2Change,
  onSameSourceChange,
  onContinue,
}: Props) {
  const canContinue = source1 !== null && (sameSource || source2 !== null);

  return (
    <div>
      <div className="section-header">STEP 1 — LOAD DATA SOURCES</div>
      <div className="source-loader">
        <UploadPanel
          title="SOURCE 01"
          source={source1}
          onSourceChange={onSource1Change}
        />
        <UploadPanel
          title="SOURCE 02"
          source={source2}
          onSourceChange={onSource2Change}
          disabled={sameSource}
        />
        <div style={{ gridColumn: '1 / -1', background: '#0f0f0f', borderTop: '1px solid #222222', padding: '16px 24px' }}>
          <label className="source-panel__self-mode">
            <input
              type="checkbox"
              checked={sameSource}
              onChange={(e) => onSameSourceChange(e.target.checked)}
              disabled={!source1}
            />
            <span className="source-panel__self-mode-label">
              SELF-COMPARISON MODE — Analyze Source 1 for internal duplicates
            </span>
          </label>
        </div>
        <div className="source-loader__footer">
          <button
            className="btn btn--primary"
            onClick={onContinue}
            disabled={!canContinue}
          >
            CONTINUE →
          </button>
        </div>
      </div>
    </div>
  );
}
