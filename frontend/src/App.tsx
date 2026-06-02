import { useState } from 'react';
import { SourceInfo, FieldPair, MatchResult, Step } from './types';
import StepIndicator from './components/StepIndicator';
import SourceLoader from './components/SourceLoader';
import IdSelector from './components/IdSelector';
import FieldMapper from './components/FieldMapper';
import RunEngine from './components/RunEngine';
import ResultsTable from './components/ResultsTable';

export default function App() {
  const [step, setStep] = useState<Step>(1);
  const [source1, setSource1] = useState<SourceInfo | null>(null);
  const [source2, setSource2] = useState<SourceInfo | null>(null);
  const [sameSource, setSameSource] = useState(false);
  const [idCol1, setIdCol1] = useState('');
  const [idCol2, setIdCol2] = useState('');
  const [fieldPairs, setFieldPairs] = useState<FieldPair[]>([{ col1: '', col2: '' }]);
  const [results, setResults] = useState<MatchResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const handleReset = () => {
    setStep(1);
    setSource1(null);
    setSource2(null);
    setSameSource(false);
    setIdCol1('');
    setIdCol2('');
    setFieldPairs([{ col1: '', col2: '' }]);
    setResults([]);
    setIsRunning(false);
  };

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__logo">DQM</div>
        <div className="app__step-bar">
          <StepIndicator currentStep={step} />
        </div>
      </header>
      <main className="app__main">
        {step === 1 && (
          <SourceLoader
            source1={source1}
            source2={source2}
            sameSource={sameSource}
            onSource1Change={setSource1}
            onSource2Change={setSource2}
            onSameSourceChange={(val) => {
              setSameSource(val);
              if (val && source1) {
                setSource2({ ...source1 });
              }
            }}
            onContinue={() => setStep(2)}
          />
        )}
        {step === 2 && source1 && (
          <IdSelector
            source1={source1}
            source2={sameSource ? source1 : source2}
            sameSource={sameSource}
            idCol1={idCol1}
            idCol2={idCol2}
            onIdCol1Change={setIdCol1}
            onIdCol2Change={setIdCol2}
            onBack={() => setStep(1)}
            onContinue={() => setStep(3)}
          />
        )}
        {step === 3 && source1 && (
          <FieldMapper
            source1={source1}
            source2={sameSource ? source1 : source2}
            sameSource={sameSource}
            fieldPairs={fieldPairs}
            onFieldPairsChange={setFieldPairs}
            onBack={() => setStep(2)}
            onContinue={() => setStep(4)}
          />
        )}
        {step === 4 && source1 && (
          <RunEngine
            source1={source1}
            source2={sameSource ? source1 : source2}
            sameSource={sameSource}
            idCol1={idCol1}
            idCol2={idCol2}
            fieldPairs={fieldPairs}
            isRunning={isRunning}
            onRunningChange={setIsRunning}
            onResults={(res) => {
              setResults(res);
              setStep(5);
            }}
            onBack={() => setStep(3)}
          />
        )}
        {step === 5 && source1 && (
          <ResultsTable
            results={results}
            source1={source1}
            source2={sameSource ? source1 : source2}
            sameSource={sameSource}
            idCol1={idCol1}
            idCol2={idCol2}
            fieldPairs={fieldPairs}
            onNewAnalysis={handleReset}
          />
        )}
      </main>
    </div>
  );
}
