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
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Заголовок */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6">
          <h2 className="text-2xl font-bold">Идентификация штаммов Lysobacter</h2>
          <p className="text-blue-100 mt-2">
            Выберите категории тестов и укажите результаты для поиска соответствующих штаммов
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {/* Выбор категории */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Выберите категорию тестов:
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {categories.map((category) => (
                <button
                  key={category.category_id}
                  type="button"
                  onClick={() => setSelectedCategory(category.category_id)}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                    selectedCategory === category.category_id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400 text-gray-700'
                  }`}
                >
                  <div className="font-medium">{category.category_name}</div>
                  {category.description && (
                    <div className="text-xs text-gray-500 mt-1">
                      {category.description}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Тесты выбранной категории */}
          {selectedCategory && tests.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Тесты категории: {categories.find(c => c.category_id === selectedCategory)?.category_name}
                </h3>
                <button
                  type="button"
                  onClick={clearAllValues}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Очистить все
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {tests.map((test) => (
                  <div key={test.test_id} className="border rounded-lg p-4 bg-gray-50">
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
                        <label className="text-sm font-medium text-gray-700">
                          {test.test_name}
                        </label>
                        <input
                          type="text"
                          placeholder="Введите текстовое значение"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
                          <p className="text-xs text-gray-500 italic">
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

          {/* Счетчик выбранных тестов */}
          {testValues.size > 0 && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-700">
                <strong>Выбрано тестов: {testValues.size}</strong>
              </div>
              <div className="text-xs text-blue-600 mt-1">
                {Array.from(testValues.values()).map(tv => {
                  const testName = tv.test_name ?? tests.find(t => t.test_id === tv.test_id)?.test_name ?? 'undefined';
                  const unit = tv.measurement_unit ?? tests.find(t => t.test_id === tv.test_id)?.measurement_unit ?? '';

                  let valueStr = '';

                  if (tv.boolean_value) {
                    valueStr = tv.boolean_value.value;
                  } else if (tv.numeric_value) {
                    if (tv.numeric_value.mode === 'exact') {
                      valueStr = `${tv.numeric_value.exact}${unit}`;
                    } else if (tv.numeric_value.range) {
                      valueStr = `${tv.numeric_value.range.min}-${tv.numeric_value.range.max}${unit}`;
                    }
                  } else if (tv.text_value) {
                    valueStr = tv.text_value;
                  }

                  return `${testName}: ${valueStr}`;
                }).join(', ')}
              </div>
            </div>
          )}

          {/* Ошибки */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-red-700 text-sm">{error}</div>
            </div>
          )}

          {/* Кнопка отправки */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={testValues.size === 0 || isLoading}
              className={`px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
                testValues.size === 0 || isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg hover:shadow-xl'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Идентификация...</span>
                </div>
              ) : (
                'Найти штаммы'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default IdentificationForm; 