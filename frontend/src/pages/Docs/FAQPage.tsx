import React from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'

interface FAQItem {
  question: string
  answer: string
  category: 'general' | 'identification' | 'technical' | 'data'
}

const FAQPage: React.FC = () => {
  const [openItems, setOpenItems] = useState<number[]>([])

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const faqData: FAQItem[] = [
    {
      category: 'general',
      question: 'Что такое LysoData-Miner и для чего он используется?',
      answer: 'LysoData-Miner — это веб-приложение для идентификации штаммов бактерий Lysobacter на основе результатов лабораторных тестов. Система содержит данные о 228 штаммах и 459 различных тестах из научных публикаций, помогая исследователям быстро и точно определить наиболее подходящие штаммы.'
    },
    // {
    //   category: 'general',
    //   question: 'Бесплатно ли использование системы?',
    //   answer: 'Да, LysoData-Miner полностью бесплатен для использования в научных и образовательных целях. Все данные получены из открытых научных публикаций.'
    // },
    {
      category: 'identification',
      question: 'Почему идентификация не дает результатов?',
      answer: 'Возможные причины: 1) Слишком мало тестов выбрано - попробуйте добавить больше тестов; 2) Результаты не совпадают ни с одним штаммом в базе; 3) Ошибка в указании результатов тестов. Рекомендуется выбрать минимум 5-10 тестов для получения значимых результатов.'
    },
    {
      category: 'identification',
      question: 'Что означают разные результаты тестов (Positive, Negative, Variable)?',
      answer: 'Positive (+) - тест дал положительный результат; Negative (-) - тест дал отрицательный результат; Variable (+/-) - результат может варьироваться в зависимости от условий или штамма; No Data - тест не проводился для данного штамма или результат неизвестен.'
    },
    {
      category: 'identification',
      question: 'Как интерпретировать процент совпадения и Confidence Score?',
      answer: 'Процент совпадения показывает долю совпавших тестов от общего числа сравниваемых тестов. Confidence Score - это комплексная оценка, учитывающая не только процент совпадения, но и количество конфликтов, полноту данных и статистическую значимость. Результаты с Confidence Score выше 80% считаются надежными.'
    },
    {
      category: 'identification',
      question: 'Что делать если получен низкий процент совпадения?',
      answer: 'Низкий процент совпадения (менее 60%) может указывать на: 1) Новый или редкий штамм, не представленный в базе; 2) Возможные ошибки в проведении тестов; 3) Необходимость дополнительных тестов. Рекомендуется провести дополнительное тестирование или обратиться к специалистам.'
    },
    {
      category: 'data',
      question: 'Откуда берутся данные в системе?',
      answer: 'Все данные получены из рецензируемых научных публикаций и международных коллекций штаммов (DSMZ, ATCC, JCM и др.). База регулярно обновляется новыми данными из свежих исследований.'
    },
    {
      category: 'data',
      question: 'Можно ли добавить собственные данные в систему?',
      answer: 'В настоящее время система не поддерживает добавление пользовательских данных. Все данные проходят научную верификацию перед включением в базу. Если у вас есть новые данные для включения, обратитесь к администратору системы.'
    },
    {
      category: 'data',
      question: 'Что означает "No Data" в результатах?',
      answer: '"No Data" означает, что для данного штамма конкретный тест не проводился или результат не был опубликован в доступных научных источниках. Это нормально, так как не все тесты проводятся для всех штаммов.'
    },
    {
      category: 'technical',
      question: 'В каких браузерах работает система?',
      answer: 'Система поддерживает все современные браузеры: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+. Для оптимальной работы рекомендуется использовать последние версии браузеров.'
    },
    {
      category: 'technical',
      question: 'Почему страница загружается медленно?',
      answer: 'Возможные причины: 1) Медленное интернет-соединение; 2) Временная нагрузка на сервер; 3) Проблемы с браузером - попробуйте очистить кэш. Обычно система отвечает менее чем за 100ms.'
    },
    {
      category: 'technical',
      question: 'Можно ли использовать систему офлайн?',
      answer: 'Нет, LysoData-Miner требует подключения к интернету для доступа к базе данных и выполнения идентификации. Система работает как веб-приложение и не имеет офлайн-режима.'
    }
  ]

  const categories = {
    general: { name: 'Общие вопросы', color: 'blue' },
    identification: { name: 'Идентификация', color: 'green' },
    data: { name: 'Данные', color: 'purple' },
    technical: { name: 'Технические вопросы', color: 'orange' }
  }

  const getCategoryItems = (category: keyof typeof categories) => 
    faqData.filter(item => item.category === category)

  const getCategoryColor = (category: keyof typeof categories) => {
    const colors = {
      blue: 'border-blue-200 bg-blue-50',
      green: 'border-green-200 bg-green-50', 
      purple: 'border-purple-200 bg-purple-50',
      orange: 'border-orange-200 bg-orange-50'
    }
    return colors[categories[category].color as keyof typeof colors]
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ❓ Часто задаваемые вопросы
        </h1>
        <p className="text-gray-600">
          Ответы на наиболее популярные вопросы о работе с LysoData-Miner
        </p>
      </div>

      <div className="space-y-8">
        {Object.entries(categories).map(([categoryKey, categoryInfo]) => {
          const categoryItems = getCategoryItems(categoryKey as keyof typeof categories)
          
          return (
            <div key={categoryKey} className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 border-b border-gray-200 pb-2">
                {categoryInfo.name}
              </h2>
              
              <div className="space-y-3">
                {categoryItems.map((item, index) => {
                  const globalIndex = faqData.indexOf(item)
                  const isOpen = openItems.includes(globalIndex)
                  
                  return (
                    <div 
                      key={globalIndex}
                      className={`border rounded-lg overflow-hidden ${getCategoryColor(categoryKey as keyof typeof categories)}`}
                    >
                      <button
                        onClick={() => toggleItem(globalIndex)}
                        className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-white/50 transition-colors"
                      >
                        <span className="font-medium text-gray-900">
                          {item.question}
                        </span>
                        {isOpen ? (
                          <ChevronDown className="h-5 w-5 text-gray-500" />
                        ) : (
                          <ChevronRight className="h-5 w-5 text-gray-500" />
                        )}
                      </button>
                      
                      {isOpen && (
                        <div className="px-6 pb-4">
                          <div className="text-gray-700 leading-relaxed">
                            {item.answer}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-12 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          Не нашли ответ на свой вопрос?
        </h3>
        <p className="text-blue-800 text-sm">
          Обратитесь к администратору системы или изучите подробную документацию 
          в разделе Help для получения дополнительной информации.
        </p>
      </div>
    </div>
  )
}

export default FAQPage 