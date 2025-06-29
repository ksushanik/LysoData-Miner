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
      {/* Заголовок теста */}
      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-gray-700">
            {test.test_name}
          </label>
          {test.measurement_unit && (
            <span className="text-xs text-gray-500 ml-1">
              ({test.measurement_unit})
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={clearValue}
          className="text-xs text-gray-400 hover:text-gray-600"
          title="Очистить значение"
        >
          ✕
        </button>
      </div>

      {/* Переключатель режима */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        <button
          type="button"
          onClick={() => handleModeChange('exact')}
          className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
            mode === 'exact'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Точное значение
        </button>
        <button
          type="button"
          onClick={() => handleModeChange('range')}
          className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
            mode === 'range'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Диапазон
        </button>
      </div>

      {/* Поле для точного значения */}
      {mode === 'exact' && (
        <div className="space-y-2">
          <input
            type="number"
            value={exactValue}
            onChange={(e) => setExactValue(e.target.value)}
            placeholder={`Введите значение (${ranges.min}-${ranges.max})`}
            min={ranges.min}
            max={ranges.max}
            step={ranges.step}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          
          {/* Быстрые кнопки для типичных значений */}
          <div className="flex gap-2 flex-wrap">
            <span className="text-xs text-gray-500">Быстрый выбор:</span>
            {[ranges.typical[0], ranges.typical[1], (ranges.typical[0] + ranges.typical[1]) / 2].map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setExactValue(val.toString())}
                className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded border text-gray-600"
              >
                {val}{test.measurement_unit}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Поля для диапазона */}
      {mode === 'range' && (
        <div className="space-y-3">
          {/* Поля ввода min и max */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Минимум</label>
              <input
                type="number"
                value={minValue}
                onChange={(e) => setMinValue(e.target.value)}
                placeholder="Мин"
                min={ranges.min}
                max={ranges.max}
                step={ranges.step}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Максимум</label>
              <input
                type="number"
                value={maxValue}
                onChange={(e) => setMaxValue(e.target.value)}
                placeholder="Макс"
                min={ranges.min}
                max={ranges.max}
                step={ranges.step}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Ползунок для диапазона на react-range */}
          <div className="px-2">
            <Range
              values={[parseFloat(minValue) || ranges.min, parseFloat(maxValue) || ranges.max]}
              step={ranges.step}
              min={ranges.min}
              max={ranges.max}
              onChange={handleRangeSliderChange}
              renderTrack={({ props, children }: { props: any; children: React.ReactNode }) => (
                <div
                  {...props}
                  className="h-2 w-full rounded bg-gray-200"
                >
                  {children}
                </div>
              )}
              renderThumb={({ props, index }: { props: any; index: number }) => (
                <div
                  {...props}
                  className={`h-4 w-4 rounded-full shadow ${index === 0 ? 'bg-blue-500' : 'bg-red-500'}`}
                />
              )}
            />

            {/* Отображение значений под ползунком */}
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>{ranges.min}{test.measurement_unit}</span>
              <span className="font-medium text-gray-700">
                {minValue && maxValue ? `${minValue} - ${maxValue} ${test.measurement_unit}` : ''}
              </span>
              <span>{ranges.max}{test.measurement_unit}</span>
            </div>
          </div>

          {/* Быстрые кнопки для типичных диапазонов */}
          <div className="flex gap-2 flex-wrap">
            <span className="text-xs text-gray-500">Быстрый выбор:</span>
            <button
              type="button"
              onClick={() => handleQuickSet(ranges.typical)}
              className="px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 rounded border text-blue-700"
            >
              Типичный ({ranges.typical[0]}-{ranges.typical[1]}{test.measurement_unit})
            </button>
            <button
              type="button"
              onClick={() => handleQuickSet([ranges.min, ranges.max])}
              className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded border text-gray-600"
            >
              Полный ({ranges.min}-{ranges.max}{test.measurement_unit})
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