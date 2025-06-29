import React, { useState, useEffect, useCallback } from 'react';
import NumericTestInput from './NumericTestInput';
import BooleanTestInput from './BooleanTestInput';
import type { 
  Test, 
  TestCategory, 
  TestValue, 
  NumericTestValue, 
  BooleanTestValue,
  IdentificationResponse 
} from '../types';

interface IdentificationFormProps {
  onResults: (results: IdentificationResponse) => void;
}

export const IdentificationForm: React.FC<IdentificationFormProps> = ({ onResults }) => {
  const [categories, setCategories] = useState<TestCategory[]>([]);
  const [tests, setTests] = useState<Test[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [testValues, setTestValues] = useState<Map<number, TestValue>>(new Map());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Загружаем категории тестов при монтировании компонента
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/tests/categories');
        if (!response.ok) throw new Error('Ошибка загрузки категорий');
        const data = await response.json();
        // API возвращает объект с полем categories
        setCategories(data.categories || []);
      } catch (err) {
        setError('Не удалось загрузить категории тестов');
        console.error('Error loading categories:', err);
      }
    };

    loadCategories();
  }, []);

  // Загружаем тесты выбранной категории
  useEffect(() => {
    if (!selectedCategory) {
      setTests([]);
      return;
    }

    const loadTests = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/tests/?category_id=${selectedCategory}`);
        if (!response.ok) throw new Error('Ошибка загрузки тестов');
        const data = await response.json();
        // API возвращает объект с полем tests
        setTests(data.tests || []);
      } catch (err) {
        setError('Не удалось загрузить тесты');
        console.error('Error loading tests:', err);
      }
    };

    loadTests();
  }, [selectedCategory]);

  // Обработчик изменения числового теста
  const handleNumericTestChange = useCallback((testId: number, test: Test, value: NumericTestValue | undefined) => {
    setTestValues(prevTestValues => {
      const newTestValues = new Map(prevTestValues);
      
      if (value) {
        newTestValues.set(testId, {
          test_id: testId,
          test_code: test.test_code,
          test_name: test.test_name,
          measurement_unit: test.measurement_unit,
          test_type: 'numeric',
          numeric_value: value
        });
      } else {
        newTestValues.delete(testId);
      }
      
      return newTestValues;
    });
  }, []);

  // Обработчик изменения булевого теста
  const handleBooleanTestChange = useCallback((testId: number, test: Test, value: BooleanTestValue | undefined) => {
    setTestValues(prevTestValues => {
      const newTestValues = new Map(prevTestValues);
      
      if (value) {
        newTestValues.set(testId, {
          test_id: testId,
          test_code: test.test_code,
          test_name: test.test_name,
          measurement_unit: test.measurement_unit,
          test_type: 'boolean',
          boolean_value: value
        });
      } else {
        newTestValues.delete(testId);
      }
      
      return newTestValues;
    });
  }, []);

  // Обработчик отправки формы для идентификации
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (testValues.size === 0) {
      setError('Выберите хотя бы один тест для идентификации');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData = {
        test_values: Array.from(testValues.values())
      };
      
      // Логирование для отладки
      console.log('Отправляем данные для идентификации:', requestData);
      console.log('Полная структура test_values:', JSON.stringify(requestData.test_values, null, 2));
      console.log('Структура test_values:', requestData.test_values.map(tv => ({
        test_id: tv.test_id,
        test_code: tv.test_code,
        test_type: tv.test_type,
        has_test_code: !!tv.test_code,
        full_object: tv
      })));

      const response = await fetch('http://localhost:8000/api/identification/identify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Ошибка ответа сервера:', errorText);
        throw new Error(`Ошибка выполнения идентификации: ${response.status}`);
      }

      const results: IdentificationResponse = await response.json();
      onResults(results);
    } catch (err) {
      setError('Не удалось выполнить идентификацию');
      console.error('Error during identification:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Очистка всех выбранных значений
  const clearAllValues = () => {
    setTestValues(new Map());
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-border">
      {/* Form Header */}
      <div className="p-6 border-b border-border">
        <h2 className="text-2xl font-bold text-foreground">Strain Identification</h2>
        <p className="text-muted-foreground mt-1">
          Select test categories and specify the results to find matching strains.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        {/* Category Selection */}
        <div className="mb-8">
          <label className="block text-base font-semibold text-foreground mb-4">
            1. Select Test Category
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <button
                key={category.category_id}
                type="button"
                onClick={() => setSelectedCategory(category.category_id)}
                className={`p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                  selectedCategory === category.category_id
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="font-semibold text-foreground">{category.category_name}</div>
                {category.description && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {category.description}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Tests for selected category */}
        {selectedCategory && tests.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-border">
              <h3 className="text-base font-semibold text-foreground">
                2. Enter Test Results for: {categories.find(c => c.category_id === selectedCategory)?.category_name}
              </h3>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {tests.map((test) => (
                <div key={test.test_id} className="rounded-lg p-4 bg-background border border-border">
                  {test.test_type === 'numeric' && (
                    <NumericTestInput
                      test={test}
                      value={testValues.get(test.test_id)?.numeric_value}
                      onChange={(value) => handleNumericTestChange(test.test_id, test, value)}
                    />
                  )}
                  
                  {test.test_type === 'boolean' && (
                    <BooleanTestInput
                      test={test}
                      value={testValues.get(test.test_id)?.boolean_value}
                      onChange={(value) => handleBooleanTestChange(test.test_id, test, value)}
                    />
                  )}
                  
                  {test.test_type === 'text' && (
                    <div className="space-y-3">
                      <label className="text-sm font-medium text-foreground">
                        {test.test_name}
                      </label>
                      <input
                        type="text"
                        placeholder="Enter text value"
                        className="w-full px-3 py-2 border border-border rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary bg-background"
                        onChange={(e) => {
                          const newTestValues = new Map(testValues);
                          if (e.target.value.trim()) {
                            newTestValues.set(test.test_id, {
                              test_id: test.test_id,
                              test_code: test.test_code,
                              test_name: test.test_name,
                              measurement_unit: test.measurement_unit,
                              test_type: 'text',
                              text_value: e.target.value.trim()
                            });
                          } else {
                            newTestValues.delete(test.test_id);
                          }
                          setTestValues(newTestValues);
                        }}
                      />
                      {test.description && (
                        <p className="text-xs text-muted-foreground italic">
                          {test.description}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 pt-6 border-t border-border flex items-center justify-between">
          <div>
            <span className="text-sm text-muted-foreground">
              {testValues.size} {testValues.size === 1 ? 'test' : 'tests'} selected
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={clearAllValues}
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:bg-muted"
              disabled={testValues.size === 0}
            >
              Clear All
            </button>
            <button
              type="submit"
              disabled={isLoading || testValues.size === 0}
              className="px-6 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:bg-primary/50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Identifying...' : 'Identify Strain'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-4 text-center text-sm text-red-600">
            {error}
          </div>
        )}
      </form>
    </div>
  );
};

export default IdentificationForm; 