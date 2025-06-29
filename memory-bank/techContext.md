# Technical Context - Lysobacter Database

## Технологический стек

### Основная СУБД
- **PostgreSQL 12+** - основная система управления базами данных
- **psql** - клиент командной строки для PostgreSQL
- **pg_dump/pg_restore** - инструменты резервного копирования

### Языки программирования
- **SQL** - создание схемы, представлений, функций и процедур
- **Python 3.8+** - скрипты импорта данных и автоматизации
- **Bash** - скрипты установки и настройки системы

### Python библиотеки
- **psycopg2-binary** - PostgreSQL адаптер для Python
- **pandas** - обработка и анализ данных
- **openpyxl** - работа с Excel файлами
- **xlsxwriter** - создание Excel файлов
- **python-dateutil** - парсинг дат в различных форматах

### Инструменты автоматизации
- **Make** - автоматизация сборки и управления проектом
- **Git** - система контроля версий
- **Shell scripts** - автоматизация операций развертывания

## Архитектура базы данных

### Схема: lysobacter
Все объекты базы данных находятся в отдельной схеме `lysobacter` для изоляции от системных объектов.

### Основные компоненты

#### 1. Справочные таблицы (Reference Tables)
```sql
-- Категории тестов
test_categories (category_id, category_name, description, sort_order)

-- Определения тестов  
tests (test_id, category_id, test_name, test_code, test_type, description, measurement_unit)

-- Возможные значения для булевых тестов
test_values (value_id, test_id, value_code, value_name, description)

-- Источники данных
data_sources (source_id, source_name, source_type, contact_info)

-- Номера коллекций
collection_numbers (collection_number_id, collection_code, collection_number, collection_name)
```

#### 2. Основные сущности (Core Entities)
```sql
-- Штаммы бактерий
strains (strain_id, strain_identifier, scientific_name, common_name, description, 
         isolation_source, isolation_location, isolation_date, source_id, notes)

-- Связи штаммов с коллекциями (M:N)
strain_collections (strain_id, collection_number_id, is_primary, notes)
```

#### 3. Результаты тестов (Test Results)
```sql
-- Булевы результаты (+, -, +/-, н.д.)
test_results_boolean (result_id, strain_id, test_id, value_id, notes, confidence_level, tested_date)

-- Числовые результаты (температура, pH и т.д.)
test_results_numeric (result_id, strain_id, test_id, value_type, numeric_value, 
                      measurement_unit, notes, confidence_level, tested_date)

-- Текстовые результаты (свободная форма)
test_results_text (result_id, strain_id, test_id, text_value, notes, confidence_level, tested_date)
```

#### 4. Аудит и история (Audit Trail)
```sql
-- Журнал изменений
audit_log (log_id, table_name, record_id, operation, old_values, new_values, changed_by, changed_at)
```

### Типы данных

#### Значения булевых тестов
- `+` (Positive) - положительный результат
- `-` (Negative) - отрицательный результат  
- `+/-` (Intermediate) - промежуточный/переменный результат
- `n.d.` (No Data) - данные отсутствуют

#### Типы числовых значений  
- `minimum` - минимальное значение диапазона
- `maximum` - максимальное значение диапазона
- `optimal` - оптимальное значение
- `single` - единичное измерение

#### Уровни достоверности
- `high` - высокая достоверность (экспериментальные данные)
- `medium` - средняя достоверность (некоторая неопределенность)
- `low` - низкая достоверность (литературные данные)

## Индексы и производительность

### Первичные индексы
- Автоматические индексы на первичные ключи
- Автоматические индексы на внешние ключи
- Уникальные индексы на альтернативные ключи

### Производительные индексы
```sql
-- Поиск штаммов
CREATE INDEX idx_strains_identifier ON lysobacter.strains(strain_identifier);
CREATE INDEX idx_strains_active ON lysobacter.strains(is_active);

-- Поиск по тестам
CREATE INDEX idx_tests_category ON lysobacter.tests(category_id);
CREATE INDEX idx_tests_type ON lysobacter.tests(test_type);
CREATE INDEX idx_tests_code ON lysobacter.tests(test_code);

-- Результаты тестов
CREATE INDEX idx_results_boolean_strain ON lysobacter.test_results_boolean(strain_id);
CREATE INDEX idx_results_boolean_test ON lysobacter.test_results_boolean(test_id);
CREATE INDEX idx_results_numeric_strain ON lysobacter.test_results_numeric(strain_id);
CREATE INDEX idx_results_numeric_test ON lysobacter.test_results_numeric(test_id);
```

### Полнотекстовый поиск
```sql
CREATE INDEX idx_strains_text_search ON lysobacter.strains USING gin(
    to_tsvector('english', 
        coalesce(strain_identifier, '') || ' ' || 
        coalesce(scientific_name, '') || ' ' || 
        coalesce(description, '')
    )
);
```

## Представления (Views)

### Основные представления
- **v_strains_complete** - полная информация о штаммах с номерами коллекций
- **v_test_results_summary** - объединенный вид всех результатов тестов
- **v_category_statistics** - статистика по категориям тестов
- **v_test_completion** - процент завершенности тестов
- **v_strain_completeness** - полнота данных по штаммам

## Функции базы данных

### Поисковые функции
```sql
-- Поиск с настраиваемой погрешностью
search_strains_with_tolerance(criteria JSONB, tolerance INTEGER)

-- Получение профиля тестов штамма
get_strain_test_profile(strain_id INTEGER)
```

### Функции валидации
```sql
-- Проверка целостности данных
validate_strain_data()
```

### Функции импорта
```sql  
-- Массовый импорт результатов тестов
bulk_import_strain_results(strain_identifier VARCHAR, test_results JSONB)
```

## Автоматизация и скрипты

### Bash скрипты
- **setup_database.sh** - полная установка и настройка БД
- Поддержка параметров командной строки (--help, --verify, --clean)
- Автоматическая проверка зависимостей
- Цветной вывод и логирование

### Python скрипты
- **import_excel.py** - импорт данных из Excel файлов
- Поддержка различных форматов Excel
- Валидация данных при импорте
- Генерация шаблонов для импорта
- Подробное логирование операций

### Makefile команды
```bash
# Установка и настройка
make setup                    # Полная установка
make setup-db                 # Только база данных
make install-deps            # Python зависимости

# Управление данными
make import-sample           # Загрузка примеров данных
make generate-template       # Создание Excel шаблона
make import-excel-all EXCEL_FILE=path  # Импорт из Excel

# Мониторинг и отчеты
make stats                   # Статистика БД
make show-categories         # Категории тестов  
make show-completion         # Завершенность тестов
make validate               # Проверка целостности

# Поиск и анализ
make search-strain STRAIN_ID=id    # Поиск штамма
make show-strain-profile STRAIN_ID=id  # Профиль штамма

# Обслуживание
make backup                  # Резервная копия
make psql                   # Подключение к БД
```

## Безопасность и права доступа

### Пользователи базы данных
- **lysobacter_user** - основной пользователь для работы с данными
- Минимальные необходимые права (не superuser)
- Доступ только к схеме lysobacter

### Аудит изменений
- Автоматическое логирование всех изменений
- Triggers для отслеживания UPDATE операций
- Хранение JSON diff в audit_log таблице

## Резервное копирование

### Стратегия backup
- Регулярные дампы через pg_dump
- Именование файлов с timestamp
- Сжатие больших дампов
- Проверка целостности backup'ов

### Восстановление
- Полное восстановление из дампа
- Возможность восстановления отдельных таблиц
- Тестирование процедур восстановления

## Мониторинг и метрики

### Ключевые метрики
- Количество штаммов и результатов тестов
- Процент завершенности данных  
- Производительность запросов
- Размер базы данных и индексов

### Инструменты мониторинга
- SQL запросы для получения статистики
- Представления для анализа полноты данных
- Функции валидации для проверки целостности

## Совместимость и зависимости

### Минимальные требования
- **PostgreSQL 12+** (для поддержки современных возможностей)
- **Python 3.8+** (для современных библиотек)
- **psql client** (для командной строки)

### Опциональные компоненты
- **pgAdmin** - графический интерфейс управления
- **DBeaver** - универсальный клиент БД
- **Jupyter Notebook** - для аналитики данных

## Развитие и расширение

### Планируемые улучшения
1. **Web интерфейс** - для удобного управления данными
2. **REST API** - для интеграции с внешними системами
3. **Расширенная аналитика** - статистические функции
4. **Геномные данные** - интеграция с секвенированием
5. **Изображения** - хранение микрофотографий

### Масштабируемость  
- **Партиционирование** - для больших таблиц результатов
- **Read replicas** - для аналитических запросов
- **Кэширование** - для часто используемых данных
- **Асинхронные операции** - для массового импорта 