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
  const options = [
    { value: '+', label: 'Положительный', color: 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200' },
    { value: '-', label: 'Отрицательный', color: 'bg-red-100 text-red-800 border-red-300 hover:bg-red-200' },
    { value: '+/-', label: 'Переменный', color: 'bg-yellow-100 text-yellow-800 border-yellow-300 hover:bg-yellow-200' },
    { value: 'n.d.', label: 'Нет данных', color: 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200' }
  ] as const;

  const handleValueChange = (newValue: '+' | '-' | '+/-' | 'n.d.') => {
    if (value?.value === newValue) {
      // Если значение уже выбрано, снимаем выбор
      onChange(undefined);
    } else {
      onChange({ value: newValue });
    }
  };

  const clearValue = () => {
    onChange(undefined);
  };

  return (
    <div className={`space-y-3 ${className}`}>
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

      {/* Кнопки выбора значений */}
      <div className="grid grid-cols-2 gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => handleValueChange(option.value)}
            className={`
              py-3 px-4 rounded-lg border-2 transition-all duration-200 text-sm font-medium
              ${value?.value === option.value 
                ? `${option.color} ring-2 ring-offset-1 ring-blue-500` 
                : `${option.color} opacity-60`
              }
            `}
          >
            <div className="flex items-center justify-center space-x-2">
              <span className="text-lg font-bold">
                {option.value}
              </span>
              <span className="text-xs">
                {option.label}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Описание выбранного значения */}
      {value && (
        <div className="text-center">
          <span className="inline-block px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
            Выбрано: {options.find(opt => opt.value === value.value)?.label}
          </span>
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

export default BooleanTestInput; 