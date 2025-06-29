import React from 'react';
import type { IdentificationResponse } from '../types';

interface IdentificationResultsProps {
  results: IdentificationResponse;
  onClear: () => void;
}

export const IdentificationResults: React.FC<IdentificationResultsProps> = ({
  results,
  onClear
}) => {
  if (!results || results.results.length === 0) {
    return (
      <div className="max-w-4xl mx-auto mt-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <div className="text-yellow-600 text-lg font-medium mb-2">
            Штаммы не найдены
          </div>
          <p className="text-yellow-700 text-sm">
            По указанным параметрам тестов не удалось найти соответствующие штаммы. 
            Попробуйте изменить критерии поиска или уменьшить количество тестов.
          </p>
          <button
            onClick={onClear}
            className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Новый поиск
          </button>
        </div>
      </div>
    );
  }

  const getMatchStatusColor = (status: string) => {
    switch (status) {
      case 'match':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'partial_match':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'mismatch':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'not_found':
        return 'bg-gray-100 text-gray-600 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-300';
    }
  };

  const getMatchStatusLabel = (status: string) => {
    switch (status) {
      case 'match':
        return '100% совпадение';
      case 'partial_match':
        return 'В пределах 15%';
      case 'mismatch':
        return 'Несовпадение';
      case 'not_found':
        return 'Нет данных';
      default:
        return status;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Высокая';
    if (confidence >= 0.5) return 'Средняя';
    return 'Низкая';
  };

  return (
    <div className="max-w-6xl mx-auto mt-8">
      {/* Заголовок результатов */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-6">
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Результаты идентификации</h2>
              <p className="text-green-100 mt-1">
                Найдено {results.total_results} штаммов за {results.execution_time_ms}мс
              </p>
            </div>
            <button
              onClick={onClear}
              className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors"
            >
              Новый поиск
            </button>
          </div>
          
          {/* Сводка по запросу */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="text-sm text-green-100">Всего тестов</div>
              <div className="text-xl font-bold">{results.query_summary.total_test_values}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="text-sm text-green-100">Булевые</div>
              <div className="text-xl font-bold">{results.query_summary.boolean_tests}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="text-sm text-green-100">Числовые</div>
              <div className="text-xl font-bold">{results.query_summary.numeric_tests}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="text-sm text-green-100">Текстовые</div>
              <div className="text-xl font-bold">{results.query_summary.text_tests}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Список результатов */}
      <div className="space-y-6">
        {results.results.map((result, index) => (
          <div key={result.strain_id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Заголовок штамма */}
            <div className="bg-gray-50 border-b p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    #{index + 1}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">
                      {result.strain_identifier}
                    </h3>
                    <p className="text-gray-600">{result.scientific_name}</p>
                    {result.common_name && (
                      <p className="text-sm text-gray-500">{result.common_name}</p>
                    )}
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Совпадение:</span>
                    <span className="text-xl font-bold text-blue-600">
                      {result.match_percentage}%
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-sm text-gray-500">Уверенность:</span>
                    <span className={`text-sm font-medium ${getConfidenceColor(result.confidence_score)}`}>
                      {getConfidenceLabel(result.confidence_score)} ({result.confidence_score.toFixed(2)})
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Статистика */}
              <div className="mt-3 grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">
                    Совпадений: <strong>{result.matching_tests}</strong>
                  </span>
                </div>
                {result.partial_matching_tests > 0 && (
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">
                      Частичных: <strong>{result.partial_matching_tests}</strong>
                    </span>
                  </div>
                )}
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">
                    Конфликтов: <strong>{result.conflicting_tests}</strong>
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                  <span className="text-sm text-gray-600">
                    Всего тестов: <strong>{result.total_tests}</strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Детали тестов */}
            <div className="p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                Детали сравнения тестов:
              </h4>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                {result.details.map((detail, detailIndex) => (
                  <div
                    key={detailIndex}
                    className={`border rounded-lg p-3 ${getMatchStatusColor(detail.match_status)}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{detail.test_name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getMatchStatusColor(detail.match_status)}`}>
                        {getMatchStatusLabel(detail.match_status)}
                      </span>
                    </div>
                    
                    <div className="text-xs space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Ваш результат:</span>
                        <span className="font-medium">{detail.query_result}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Результат штамма:</span>
                        <span className="font-medium">
                          {detail.strain_result || 'Нет данных'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Дополнительная информация о штамме */}
              {result.isolation_source && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <div className="text-sm">
                    <span className="font-medium text-blue-700">Источник выделения:</span>
                    <span className="ml-2 text-blue-600">{result.isolation_source}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Информация о методике */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">
          О методике идентификации
        </h4>
        <div className="text-xs text-blue-700 space-y-1">
          <p>• <strong className="text-green-600">100% совпадение</strong> - точное соответствие результатов тестов</p>
          <p>• <strong className="text-yellow-600">В пределах 15%</strong> - результат отличается не более чем на 15% от значения</p>
          <p>• <strong className="text-red-600">Несовпадение</strong> - результаты значительно не совпадают</p>
          <p>• <strong className="text-gray-600">Нет данных</strong> - для штамма отсутствуют данные по этому тесту</p>
          <p>• <strong>Процент совпадения</strong> рассчитывается с весами: 100% за точное совпадение, 85% за попадание в 15%</p>
          <p>• <strong>Уверенность</strong> учитывает качество совпадений и количество конфликтов</p>
        </div>
      </div>
    </div>
  );
};

export default IdentificationResults; 