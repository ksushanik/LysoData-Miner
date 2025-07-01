import React from 'react'
import { Link } from 'react-router-dom'
import { HelpCircle, ExternalLink } from 'lucide-react'
import { useStats } from '@/hooks/useStats'

const format = (n?: number) => (n === undefined ? '–' : n.toLocaleString('ru-RU'))

const QuickHelpCard: React.FC = () => {
  const { stats } = useStats()

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        <HelpCircle className="h-6 w-6 text-blue-600 mr-3" />
        <h3 className="text-lg font-semibold text-gray-900">Быстрая справка</h3>
      </div>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-gray-900 mb-2">🚀 Как начать работу:</h4>
          <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
            <li>Перейдите в раздел <Link to="/identify" className="text-blue-600 hover:underline">"Identify Strain"</Link></li>
            <li>Выберите категории тестов (Biochemical, Physiological, etc.)</li>
            <li>Укажите результаты ваших лабораторных тестов</li>
            <li>Получите список наиболее подходящих штаммов</li>
          </ol>
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-2">📊 Просмотр данных:</h4>
          <p className="text-sm text-gray-600 mb-2">
            Используйте <Link to="/strains" className="text-blue-600 hover:underline">"Browse Strains"</Link> для изучения базы данных:
          </p>
          <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside ml-4">
            <li>{format(stats?.total_species)} различных вида Lysobacter</li>
            <li>{format(stats?.total_strains)} штаммов с детальной информацией</li>
            <li>{format(stats?.total_test_results)} результатов тестов</li>
          </ul>
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-2">💡 Полезные советы:</h4>
          <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
            <li>Чем больше тестов вы укажете, тем точнее будет идентификация</li>
            <li>Используйте функцию сравнения для анализа различий между штаммами</li>
            <li>Все данные основаны на научных публикациях</li>
          </ul>
        </div>

        <div className="pt-4 border-t border-gray-200 space-y-2">
          <Link 
            to="/help" 
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 block"
          >
            <span>Подробное руководство</span>
            <ExternalLink className="h-4 w-4 ml-1" />
          </Link>
          <Link 
            to="/faq" 
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 block"
          >
            <span>Часто задаваемые вопросы</span>
            <ExternalLink className="h-4 w-4 ml-1" />
          </Link>
        </div>
      </div>
    </div>
  )
}

export default QuickHelpCard 