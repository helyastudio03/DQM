import { Step } from '../types';

interface Props {
  currentStep: Step;
}

const LABELS = ['SOURCES', 'IDENTIFIERS', 'MAPPING', 'EXECUTION', 'RESULTS'];

export default function StepIndicator({ currentStep }: Props) {
  return (
    <nav className="step-indicator">
      {LABELS.map((label, i) => {
        const num = (i + 1) as Step;
        const isActive = num === currentStep;
        const isDone = num < currentStep;
        return (
          <div
            key={num}
            className={
              'step-indicator__item' +
              (isActive ? ' step-indicator__item--active' : '') +
              (isDone ? ' step-indicator__item--done' : '')
            }
          >
            {isDone ? (
              <span className="step-indicator__check">✓</span>
            ) : (
              <span className="step-indicator__num">{num}</span>
            )}
            {label}
          </div>
        );
      })}
    </nav>
  );
}
