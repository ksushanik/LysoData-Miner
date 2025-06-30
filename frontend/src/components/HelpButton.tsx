import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { HelpCircle, X, ExternalLink } from 'lucide-react'

const HelpButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Floating Help Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 shadow-lg transition-colors duration-200 group"
          title="Получить помощь"
        >
          <HelpCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
        </button>
      </div>

      {/* Help Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 relative">
            <button
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                🆘 Нужна помощь?
              </h3>
              <p className="text-gray-600 text-sm">
                Выберите подходящий раздел для получения справки:
              </p>
            </div>

            <div className="space-y-3">
              <Link
                to="/faq"
                onClick={() => setIsOpen(false)}
                className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">FAQ</div>
                    <div className="text-sm text-gray-600">Частые вопросы и ответы</div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400" />
                </div>
              </Link>

              <Link
                to="/help"
                onClick={() => setIsOpen(false)}
                className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">Руководство пользователя</div>
                    <div className="text-sm text-gray-600">Полная документация системы</div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400" />
                </div>
              </Link>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="font-medium text-blue-900 text-sm mb-1">Быстрая помощь:</div>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Для идентификации: выберите минимум 5-10 тестов</li>
                  <li>• Используйте разные категории тестов для точности</li>
                  <li>• Результаты с confidence score 80%+ надежны</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default HelpButton 