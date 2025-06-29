import React, { useState, useEffect } from 'react';
import type { Test, NumericTestValue } from '../types';
import { Range } from 'react-range';

interface NumericTestInputProps {
  test: Test;
  value?: NumericTestValue;
  onChange: (value: NumericTestValue | undefined) => void;
  className?: string;
}

export const NumericTestInput: React.FC<NumericTestInputProps> = ({
  test,
  value,
  onChange,
  className = ""
}) => {
  const [mode, setMode] = useState<'exact' | 'range'>(value?.mode || 'exact');
  const [exactValue, setExactValue] = useState<string>(value?.exact?.toString() || '');
  const [minValue, setMinValue] = useState<string>(value?.range?.min?.toString() || '');
  const [maxValue, setMaxValue] = useState<string>(value?.range?.max?.toString() || '');

  // Определяем разумные диапазоны на основе типа теста
  const getTestRanges = (testCode: string) => {
    switch (testCode) {
      case 'temperature':
        return { min: -10, max: 60, step: 1, typical: [15, 42] };
      case 'ph_level':
        return { min: 0, max: 14, step: 0.1, typical: [6, 11] };
      case 'salt_tolerance':
        return { min: 0, max: 10, step: 0.1, typical: [0, 5] };
      case 'gc_content':
        return { min: 0, max: 100, step: 0.1, typical: [40, 70] };
      default:
        return { min: 0, max: 100, step: 0.1, typical: [0, 50] };
    }
  };

  const ranges = getTestRanges(test.test_code);

  // Обновляем значение при изменении режима или полей
  useEffect(() => {
    let newValue: NumericTestValue | undefined;

    if (mode === 'exact' && exactValue !== '') {
      const num = parseFloat(exactValue);
      if (!isNaN(num)) {
        newValue = { mode: 'exact', exact: num };
      }
    } else if (mode === 'range' && minValue !== '' && maxValue !== '') {
      const min = parseFloat(minValue);
      const max = parseFloat(maxValue);
      if (!isNaN(min) && !isNaN(max) && min <= max) {
        newValue = { mode: 'range', range: { min, max } };
      }
    }

    onChange(newValue);
  }, [mode, exactValue, minValue, maxValue]);

  const handleModeChange = (newMode: 'exact' | 'range') => {
    setMode(newMode);
    
    // При переключении на диапазон, устанавливаем типичные значения
    if (newMode === 'range' && minValue === '' && maxValue === '') {
      setMinValue(ranges.typical[0].toString());
      setMaxValue(ranges.typical[1].toString());
    }
    
    // При переключении на точное значение, очищаем поля диапазона
    if (newMode === 'exact') {
      setMinValue('');
      setMaxValue('');
    }
  };

  const handleRangeSliderChange = (values: number[]) => {
    const [min, max] = values;
    setMinValue(min.toString());
    setMaxValue(max.toString());
  };

  const handleQuickSet = (values: number[]) => {
    if (mode === 'range') {
      setMinValue(values[0].toString());
      setMaxValue(values[1].toString());
    } else {
      setExactValue(values[0].toString());
    }
  };

  const clearValue = () => {
    setExactValue('');
    setMinValue('');
    setMaxValue('');
    onChange(undefined);
  };

  return (
    <div className={`space-y-4 ${className}`}>
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

      {/* Mode Switcher */}
      <div className="flex bg-muted rounded-lg p-1">
        <button
          type="button"
          onClick={() => handleModeChange('exact')}
          className={`flex-1 py-1.5 px-3 text-sm font-medium rounded-md transition-colors ${
            mode === 'exact'
              ? 'bg-white text-primary shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Exact
        </button>
        <button
          type="button"
          onClick={() => handleModeChange('range')}
          className={`flex-1 py-1.5 px-3 text-sm font-medium rounded-md transition-colors ${
            mode === 'range'
              ? 'bg-white text-primary shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Range
        </button>
      </div>

      {/* Exact Value Input */}
      {mode === 'exact' && (
        <div className="space-y-2">
          <input
            type="number"
            value={exactValue}
            onChange={(e) => setExactValue(e.target.value)}
            placeholder={`Enter value (${ranges.min}-${ranges.max})`}
            min={ranges.min}
            max={ranges.max}
            step={ranges.step}
            className="w-full px-3 py-2 border border-border bg-background rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
          />
          
          {/* Quick Set Buttons */}
          <div className="flex gap-2 flex-wrap items-center">
            <span className="text-xs text-muted-foreground">Quick set:</span>
            {[ranges.typical[0], ranges.typical[1], (ranges.typical[0] + ranges.typical[1]) / 2].map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setExactValue(val.toString())}
                className="px-2 py-0.5 text-xs bg-muted hover:bg-border rounded-full border-border text-muted-foreground"
              >
                {val}{test.measurement_unit}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Range Inputs */}
      {mode === 'range' && (
        <div className="space-y-3">
          {/* Min & Max Inputs */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Min</label>
              <input
                type="number"
                value={minValue}
                onChange={(e) => setMinValue(e.target.value)}
                placeholder="Min"
                min={ranges.min}
                max={ranges.max}
                step={ranges.step}
                className="w-full px-3 py-2 border border-border bg-background rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Max</label>
              <input
                type="number"
                value={maxValue}
                onChange={(e) => setMaxValue(e.target.value)}
                placeholder="Max"
                min={ranges.min}
                max={ranges.max}
                step={ranges.step}
                className="w-full px-3 py-2 border border-border bg-background rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              />
            </div>
          </div>

          {/* Range Slider */}
          <div className="px-2 pt-2">
            <Range
              values={[parseFloat(minValue) || ranges.min, parseFloat(maxValue) || ranges.max]}
              step={ranges.step}
              min={ranges.min}
              max={ranges.max}
              onChange={handleRangeSliderChange}
              renderTrack={({ props, children }) => (
                <div
                  {...props}
                  className="h-1.5 w-full rounded-full bg-muted"
                >
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{
                      width: `${((parseFloat(maxValue) || ranges.max) - (parseFloat(minValue) || ranges.min)) / (ranges.max - ranges.min) * 100}%`,
                      marginLeft: `${((parseFloat(minValue) || ranges.min) - ranges.min) / (ranges.max - ranges.min) * 100}%`
                    }}
                  />
                </div>
              )}
              renderThumb={({ props }) => (
                <div
                  {...props}
                  className="h-4 w-4 rounded-full bg-white border-2 border-primary shadow"
                />
              )}
            />

            {/* Range Labels */}
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>{ranges.min}{test.measurement_unit}</span>
              <span className="font-medium text-foreground">
                {minValue && maxValue ? `${minValue} - ${maxValue}` : ''}
              </span>
              <span>{ranges.max}{test.measurement_unit}</span>
            </div>
          </div>

          {/* Quick Range Buttons */}
          <div className="flex gap-2 flex-wrap items-center">
            <span className="text-xs text-muted-foreground">Quick set:</span>
            <button
              type="button"
              onClick={() => handleQuickSet(ranges.typical)}
              className="px-2 py-0.5 text-xs bg-muted hover:bg-border rounded-full border-border text-muted-foreground"
            >
              Typical ({ranges.typical.join('-')}{test.measurement_unit})
            </button>
          </div>
        </div>
      )}

      {/* Описание теста */}
      {test.description && (
        <p className="text-xs text-gray-500 italic">
          {test.description}
        </p>
      )}
    </div>
  );
};

export default NumericTestInput; 