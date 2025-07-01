import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  BookOpen, 
  HelpCircle, 
  GraduationCap,
  Settings,
  Bug,
  Sparkles,
  ExternalLink
} from 'lucide-react'
import { useStats, DashboardStats } from '@/hooks/useStats'

interface WikiSection {
  id: string
  title: string
  icon: React.ComponentType<any>
  content: React.ReactNode
}

const WikiPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('overview')
  const { stats } = useStats()

  const sections: WikiSection[] = [
    {
      id: 'overview',
      title: 'Обзор системы',
      icon: BookOpen,
      content: <OverviewSection stats={stats} />
    },
    {
      id: 'getting-started',
      title: 'Начало работы',
      icon: Sparkles,
      content: <GettingStartedSection />
    },
    {
      id: 'identification',
      title: 'Идентификация штаммов',
      icon: GraduationCap,
      content: <IdentificationSection />
    },
    {
      id: 'browsing',
      title: 'Просмотр данных',
      icon: HelpCircle,
      content: <BrowsingSection stats={stats} />
    },
    {
      id: 'troubleshooting',
      title: 'Решение проблем',
      icon: Bug,
      content: <TroubleshootingSection />
    },
    {
      id: 'technical',
      title: 'Техническая информация',
      icon: Settings,
      content: <TechnicalSection stats={stats} />
    }
  ]

  const currentSection = sections.find(s => s.id === activeSection)

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📚 LysoData-Miner Wiki
        </h1>
        <p className="text-gray-600 mb-4">
          Полное руководство пользователя для системы идентификации штаммов Lysobacter
        </p>
        
        <div className="flex gap-4">
          <Link 
            to="/faq" 
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <HelpCircle className="h-4 w-4 mr-2" />
            Часто задаваемые вопросы
          </Link>
          
          <a 
            href="#overview" 
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
          >
            <BookOpen className="h-4 w-4 mr-2" />
            Читать руководство
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-24">
            <h3 className="font-semibold text-gray-900 mb-4">Содержание</h3>
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-md transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-3" />
                    {section.title}
                  </button>
                )
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            {currentSection && (
              <>
                <div className="flex items-center mb-6">
                  <currentSection.icon className="h-6 w-6 mr-3 text-blue-600" />
                  <h2 className="text-2xl font-bold text-gray-900">
                    {currentSection.title}
                  </h2>
                </div>
                <div className="prose max-w-none">
                  {currentSection.content}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Section Components
interface OverviewProps { stats: DashboardStats | null }

const format = (n?: number) => (n === undefined ? '–' : n.toLocaleString('ru-RU'))

const OverviewSection: React.FC<OverviewProps> = ({ stats }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Что такое LysoData-Miner?</h3>
      <p className="text-gray-700 mb-4">
        LysoData-Miner — это веб-приложение для идентификации штаммов бактерий Lysobacter
        на основе результатов лабораторных тестов. Система содержит данные о {format(stats?.total_strains)} штаммах
        и {format(stats?.total_test_results)} результатах тестов из научных публикаций.
      </p>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-2">Основные возможности:</h4>
      <ul className="list-disc pl-6 space-y-2 text-gray-700">
        <li><strong>Идентификация штаммов</strong> — определение наиболее подходящих штаммов по результатам тестов</li>
        <li><strong>Просмотр базы данных</strong> — изучение информации о штаммах по видам</li>
        <li><strong>Сравнение штаммов</strong> — анализ различий между несколькими штаммами</li>
        <li><strong>Научная документация</strong> — ссылки на источники данных</li>
      </ul>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-2">Данные системы:</h4>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{format(stats?.total_strains)}</div>
          <div className="text-sm text-gray-600">штаммов Lysobacter</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{format(stats?.total_categories)}</div>
          <div className="text-sm text-gray-600">категорий тестов</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{format(stats?.total_test_results)}</div>
          <div className="text-sm text-gray-600">результатов тестов</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{format(stats?.total_sources)}</div>
          <div className="text-sm text-gray-600">научных источника</div>
        </div>
      </div>
    </div>
  </div>
)

const GettingStartedSection: React.FC = () => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Быстрый старт</h3>
      <p className="text-gray-700 mb-4">
        Для начала работы с LysoData-Miner выполните следующие шаги:
      </p>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Шаг 1: Знакомство с интерфейсом</h4>
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <p className="text-gray-700">
          Главная страница (Dashboard) содержит общую статистику системы и быстрые ссылки 
          на основные функции.
        </p>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Шаг 2: Выберите задачу</h4>
      <div className="space-y-3">
        <div className="border border-blue-200 bg-blue-50 p-4 rounded-lg">
          <h5 className="font-semibold text-blue-900">🔬 Идентификация штамма</h5>
          <p className="text-blue-700 text-sm">
            Перейдите на страницу "Identify Strain", если у вас есть результаты лабораторных 
            тестов и вы хотите найти подходящие штаммы.
          </p>
        </div>
        <div className="border border-green-200 bg-green-50 p-4 rounded-lg">
          <h5 className="font-semibold text-green-900">📊 Просмотр данных</h5>
          <p className="text-green-700 text-sm">
            Перейдите на страницу "Browse Strains", чтобы изучить информацию о штаммах 
            по видам и коллекциям.
          </p>
        </div>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Шаг 3: Изучите результаты</h4>
      <p className="text-gray-700">
        Все результаты содержат подробную информацию о штаммах, включая научные названия, 
        номера коллекций и ссылки на источники данных.
      </p>
    </div>

    <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
      <h5 className="font-semibold text-yellow-900 mb-2">💡 Совет</h5>
      <p className="text-yellow-800 text-sm">
        Начните с просмотра примеров на Dashboard, чтобы понять возможности системы.
      </p>
    </div>
  </div>
)

const IdentificationSection: React.FC = () => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Как работает идентификация</h3>
      <p className="text-gray-700 mb-4">
        Система идентификации сравнивает ваши результаты тестов с данными в базе 
        и находит наиболее подходящие штаммы.
      </p>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Пошаговое руководство:</h4>
      <div className="space-y-4">
        <div className="flex">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">1</div>
          <div className="ml-4">
            <h5 className="font-semibold">Выберите категории тестов</h5>
            <p className="text-gray-600 text-sm">
              Biochemical, Physiological, Metabolic, Morphological, Other
            </p>
          </div>
        </div>
        
        <div className="flex">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">2</div>
          <div className="ml-4">
            <h5 className="font-semibold">Выберите конкретные тесты</h5>
            <p className="text-gray-600 text-sm">
              Из выбранных категорий появятся доступные тесты
            </p>
          </div>
        </div>
        
        <div className="flex">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">3</div>
          <div className="ml-4">
            <h5 className="font-semibold">Укажите результаты</h5>
            <p className="text-gray-600 text-sm">
              Positive (+), Negative (-), Variable (+/-), или No Data
            </p>
          </div>
        </div>
        
        <div className="flex">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">4</div>
          <div className="ml-4">
            <h5 className="font-semibold">Получите результаты</h5>
            <p className="text-gray-600 text-sm">
              Система покажет наиболее подходящие штаммы с процентом совпадения
            </p>
          </div>
        </div>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Интерпретация результатов:</h4>
      <div className="space-y-3">
        <div className="bg-green-50 border border-green-200 p-3 rounded-lg">
          <strong className="text-green-900">Процент совпадения:</strong>
          <span className="text-green-700 ml-2">Количество совпавших тестов от общего числа</span>
        </div>
        <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
          <strong className="text-blue-900">Confidence Score:</strong>
          <span className="text-blue-700 ml-2">Комплексная оценка надежности результата</span>
        </div>
        <div className="bg-orange-50 border border-orange-200 p-3 rounded-lg">
          <strong className="text-orange-900">Конфликты:</strong>
          <span className="text-orange-700 ml-2">Количество несовпадающих результатов тестов</span>
        </div>
      </div>
    </div>
  </div>
)

interface StatsProps { stats: DashboardStats | null }

const BrowsingSection: React.FC<StatsProps> = ({ stats }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Просмотр и поиск данных</h3>
      <p className="text-gray-700 mb-4">
        Раздел "Browse Strains" позволяет изучать базу данных штаммов различными способами.
      </p>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Просмотр по видам:</h4>
      <ul className="list-disc pl-6 space-y-2 text-gray-700">
        <li>{format(stats?.total_species)} различных вида Lysobacter</li>
        <li>Количество штаммов для каждого вида</li>
        <li>Ссылки на детальную информацию о штаммах</li>
      </ul>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Информация о штаммах:</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h5 className="font-semibold mb-2">Основная информация:</h5>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Научное название</li>
            <li>• Полное название штамма</li>
            <li>• Код штамма</li>
          </ul>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h5 className="font-semibold mb-2">Дополнительные данные:</h5>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Номера коллекций</li>
            <li>• Научные источники</li>
            <li>• Результаты тестов</li>
          </ul>
        </div>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Сравнение штаммов:</h4>
      <p className="text-gray-700 mb-3">
        Используйте функцию сравнения для анализа различий между штаммами:
      </p>
      <ol className="list-decimal pl-6 space-y-2 text-gray-700">
        <li>Нажмите "Add to Compare" на интересующих штаммах</li>
        <li>Выберите до 20 штаммов для сравнения</li>
        <li>Перейдите на страницу сравнения</li>
        <li>Изучите таблицу с различиями в тестах</li>
      </ol>
    </div>
  </div>
)

const TroubleshootingSection: React.FC = () => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Часто задаваемые вопросы</h3>
    </div>

    <div className="space-y-4">
      <div className="border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">❓ Почему идентификация не дает результатов?</h4>
        <p className="text-gray-700 text-sm">
          Возможные причины: слишком мало тестов выбрано, результаты не совпадают ни с одним штаммом, 
          или ошибка в указании результатов. Попробуйте выбрать больше тестов или проверить правильность результатов.
        </p>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">❓ Что означает "No Data" в результатах?</h4>
        <p className="text-gray-700 text-sm">
          "No Data" означает, что для данного штамма этот тест не проводился или результат 
          не был опубликован в научных источниках.
        </p>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">❓ Как интерпретировать низкий процент совпадения?</h4>
        <p className="text-gray-700 text-sm">
          Низкий процент может указывать на новый штамм или ошибки в тестировании. 
          Рекомендуется провести дополнительные тесты или обратиться к специалистам.
        </p>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2">❓ Страница загружается медленно</h4>
        <p className="text-gray-700 text-sm">
          Проверьте интернет-соединение. Если проблема сохраняется, возможно временные 
          технические проблемы с сервером.
        </p>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Получение помощи:</h4>
      <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
        <p className="text-blue-900">
          Если у вас возникли проблемы, которые не описаны выше, обратитесь к администратору системы 
          или ознакомьтесь с технической документацией в разделе "Техническая информация".
        </p>
      </div>
    </div>
  </div>
)

const TechnicalSection: React.FC<StatsProps> = ({ stats }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-xl font-semibold mb-3">Техническая информация</h3>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Архитектура системы:</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h5 className="font-semibold text-blue-900">Frontend</h5>
          <p className="text-blue-700 text-sm">React + TypeScript</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h5 className="font-semibold text-green-900">Backend</h5>
          <p className="text-green-700 text-sm">FastAPI + Python</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h5 className="font-semibold text-purple-900">Database</h5>
          <p className="text-purple-700 text-sm">PostgreSQL 15</p>
        </div>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">API Endpoints:</h4>
      <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm">
        <div className="space-y-1">
          <div><span className="text-green-600">GET</span> /api/health/ - Проверка состояния системы</div>
          <div><span className="text-green-600">GET</span> /api/tests/categories - Категории тестов</div>
          <div><span className="text-green-600">GET</span> /api/species - Список видов</div>
          <div><span className="text-blue-600">POST</span> /api/identification/identify - Идентификация</div>
        </div>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Производительность:</h4>
      <ul className="list-disc pl-6 space-y-2 text-gray-700">
        <li>Время ответа API: менее 100ms</li>
        <li>Время идентификации: около 50ms</li>
        <li>Поддержка до 100 одновременных пользователей</li>
        <li>База данных: {format(stats?.total_strains)} штаммов, {format(stats?.total_test_results)} результатов тестов</li>
      </ul>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Системные требования:</h4>
      <div className="bg-gray-50 p-4 rounded-lg">
        <h5 className="font-semibold mb-2">Поддерживаемые браузеры:</h5>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Chrome 90 и выше</li>
          <li>• Firefox 88 и выше</li>
          <li>• Safari 14 и выше</li>
          <li>• Edge 90 и выше</li>
        </ul>
      </div>
    </div>

    <div>
      <h4 className="text-lg font-semibold mb-3">Источники данных:</h4>
      <p className="text-gray-700 mb-3">
        Все данные получены из рецензируемых научных публикаций и международных 
        коллекций штаммов (DSMZ, ATCC, JCM и др.).
      </p>
      <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
        <p className="text-yellow-900 text-sm">
          <strong>Важно:</strong> Система предназначена для научных исследований. 
          Результаты должны быть подтверждены дополнительными методами.
        </p>
      </div>
    </div>
  </div>
)

export default WikiPage 