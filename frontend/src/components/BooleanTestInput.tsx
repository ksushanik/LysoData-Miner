import React from 'react';
import type { Test, BooleanTestValue } from '../types';

interface BooleanTestInputProps {
  test: Test;
  value?: BooleanTestValue;
  onChange: (value: BooleanTestValue | undefined) => void;
  className?: string;
}

export const BooleanTestInput: React.FC<BooleanTestInputProps> = ({
  test,
  value,
  onChange,
  className = ""
}) => {
  type OptionValue = '+' | '-' | '+/-' | 'n.d.';
  
  const options: { value: OptionValue; label: string; style: string; selectedStyle: string }[] = [
    { value: '+', label: 'Positive', style: 'border-green-500/30 hover:border-green-500/80', selectedStyle: 'bg-green-500/10 border-green-500/80' },
    { value: '-', label: 'Negative', style: 'border-red-500/30 hover:border-red-500/80', selectedStyle: 'bg-red-500/10 border-red-500/80' },
    { value: '+/-', label: 'Variable', style: 'border-yellow-500/30 hover:border-yellow-500/80', selectedStyle: 'bg-yellow-500/10 border-yellow-500/80' },
    { value: 'n.d.', label: 'Not Detected', style: 'border-border hover:border-muted-foreground/50', selectedStyle: 'bg-muted border-muted-foreground/50' }
  ];

  const handleValueChange = (newValue: OptionValue) => {
    if (value?.value === newValue) {
      onChange(undefined); // Deselect if already selected
    } else {
      onChange({ value: newValue });
    }
  };

  const clearValue = () => {
    onChange(undefined);
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Test Header */}
      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-foreground">
            {test.test_name}
          </label>
          {test.measurement_unit && (
            <span className="text-xs text-muted-foreground ml-1">
              ({test.measurement_unit})
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={clearValue}
          className="text-xs text-muted-foreground hover:text-foreground"
          title="Clear value"
        >
          ✕
        </button>
      </div>

      {/* Value Selection Buttons */}
      <div className="grid grid-cols-2 gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => handleValueChange(option.value)}
            className={`
              py-2 px-3 rounded-lg border-2 transition-all duration-200 text-sm font-medium
              ${value?.value === option.value 
                ? `${option.selectedStyle} ring-2 ring-offset-1 ring-primary` 
                : `${option.style}`
              }
            `}
          >
            <div className="flex flex-col items-center justify-center space-y-1">
              <span className="font-bold text-foreground">
                {option.label}
              </span>
              <span className="text-xs text-muted-foreground">
                ({option.value})
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Test Description */}
      {test.description && (
        <p className="text-xs text-muted-foreground italic pt-1">
          {test.description}
        </p>
      )}
    </div>
  );
};

export default BooleanTestInput;