import React, { useState } from 'react';
import IdentificationForm from '../components/IdentificationForm';
import IdentificationResultsModal from '../components/IdentificationResultsModal';
import type { IdentificationResponse } from '../types';

export const Identification: React.FC = () => {
  const [results, setResults] = useState<IdentificationResponse | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleResults = (newResults: IdentificationResponse) => {
    setResults(newResults);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Заголовок приложения */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            LysoData-Miner
          </h1>
          <p className="text-xl text-gray-600">
            Система идентификации штаммов бактерий рода Lysobacter
          </p>
          <div className="mt-4 flex items-center justify-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>228 штаммов в базе данных</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span>459 доступных тестов</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span>5 категорий анализов</span>
            </div>
          </div>
        </div>

        {/* Основной контент */}
        <IdentificationForm onResults={handleResults} />
        
        {/* Модальное окно с результатами */}
        {results && (
          <IdentificationResultsModal
            results={results}
            isOpen={isModalOpen}
            onClose={handleCloseModal}
          />
        )}

        {/* Нижний колонтитул */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              О системе
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed max-w-4xl mx-auto">
              LysoData-Miner - это веб-сервис для идентификации штаммов бактерий рода Lysobacter 
              на основе морфологических, физиологических и биохимических характеристик. 
              Система использует современные алгоритмы сравнения с автоматическим расчетом 
              степени соответствия и уверенности в результатах идентификации.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Морфологические тесты</h4>
                <p className="text-xs text-blue-700">
                  Форма колоний, пигментация, морфология клеток
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">Физиологические тесты</h4>
                <p className="text-xs text-green-700">
                  Температурные режимы, pH, рост в различных условиях
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 mb-2">Биохимические тесты</h4>
                <p className="text-xs text-purple-700">
                  Ферментативная активность, катаболизм различных субстратов
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Identification; 