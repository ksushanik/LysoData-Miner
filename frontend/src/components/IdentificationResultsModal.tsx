import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ExternalLink } from 'lucide-react';
import type { IdentificationResponse } from '../types';

interface IdentificationResultsModalProps {
  results: IdentificationResponse;
  isOpen: boolean;
  onClose: () => void;
}

export const IdentificationResultsModal: React.FC<IdentificationResultsModalProps> = ({
  results,
  isOpen,
  onClose
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const firstResultRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Навигация к карточке штамма
  const handleStrainClick = (strainId: number) => {
    onClose(); // Закрываем модальное окно
    navigate(`/strains/${strainId}`); // Переходим к карточке штамма
  };

  // Фокус на первом результате при открытии модального окна
  useEffect(() => {
    if (isOpen && firstResultRef.current) {
      firstResultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      firstResultRef.current.focus();
    }
  }, [isOpen]);

  // Закрытие по Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Закрытие по клику вне модального окна
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen || !results || results.results.length === 0) {
    return null;
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
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col"
      >
        {/* Заголовок модального окна */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Результаты идентификации</h2>
              <p className="text-green-100 mt-1">
                Найдено {results.total_results} штаммов за {results.execution_time_ms}мс
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
              aria-label="Закрыть"
            >
              <X size={24} />
            </button>
          </div>

          {/* Сводка по запросу */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white bg-opacity-20 rounded-lg p-3">
              <div className="text-sm text-green-100">Всего тестов</div>
              <div className="text-xl font-bold">{results.query_summary.total_test_values}</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-3">
              <div className="text-sm text-green-100">Булевы тесты</div>
              <div className="text-xl font-bold">{results.query_summary.boolean_tests}</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-3">
              <div className="text-sm text-green-100">Числовые тесты</div>
              <div className="text-xl font-bold">{results.query_summary.numeric_tests}</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-3">
              <div className="text-sm text-green-100">Текстовые тесты</div>
              <div className="text-xl font-bold">{results.query_summary.text_tests}</div>
            </div>
          </div>
        </div>

        {/* Содержимое с прокруткой */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {results.results.map((result, index) => (
              <div
                key={result.strain_id}
                ref={index === 0 ? firstResultRef : undefined}
                tabIndex={index === 0 ? 0 : -1}
                className="bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {/* Заголовок штамма */}
                <div className="bg-gray-50 border-b p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                        #{index + 1}
                      </div>
                      <div className="flex-1">
                        <button
                          onClick={() => handleStrainClick(result.strain_id)}
                          className="text-left group hover:bg-blue-50 rounded-lg p-2 -m-2 transition-colors w-full"
                        >
                          <div className="flex items-center space-x-2">
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                              {result.strain_identifier}
                            </h3>
                            <ExternalLink 
                              size={16} 
                              className="text-gray-400 group-hover:text-blue-500 transition-colors opacity-0 group-hover:opacity-100" 
                            />
                          </div>
                          <p className="text-gray-600 group-hover:text-gray-700 transition-colors">
                            {result.scientific_name}
                          </p>
                          {result.common_name && (
                            <p className="text-sm text-gray-500 group-hover:text-gray-600 transition-colors">
                              {result.common_name}
                            </p>
                          )}
                        </button>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm text-gray-500">Совпадение:</span>
                        <span className="text-xl font-bold text-blue-600">
                          {result.match_percentage}%
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 mb-3">
                        <span className="text-sm text-gray-500">Уверенность:</span>
                        <span className={`text-sm font-medium ${getConfidenceColor(result.confidence_score)}`}>
                          {getConfidenceLabel(result.confidence_score)} ({result.confidence_score.toFixed(2)})
                        </span>
                      </div>
                      <button
                        onClick={() => handleStrainClick(result.strain_id)}
                        className="inline-flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-3 py-1 rounded-lg transition-colors"
                      >
                        <span>Подробнее</span>
                        <ExternalLink size={14} />
                      </button>
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

        {/* Футер с кнопками */}
        <div className="border-t bg-gray-50 px-6 py-4 flex-shrink-0">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Нажмите Escape или кликните вне окна для закрытия
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              Продолжить поиск
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdentificationResultsModal; 