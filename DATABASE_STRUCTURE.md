# Структура базы данных штаммов лизобактера

## Обзор системы

База данных `lysobacter_db` спроектирована для управления штаммами бактерий лизобактера и результатами их лабораторных тестов. Система соответствует третьей нормальной форме (3NF) и включает 11 таблиц, 5 представлений и 5 функций.

### Технические характеристики

- **СУБД**: PostgreSQL (latest)
- **Схема**: `lysobacter`
- **Кодировка**: UTF-8
- **Порт**: 5434 (Docker контейнер)
- **База данных**: `lysobacter_db`
- **Пользователь**: `lysobacter_user`

## 📊 Архитектура базы данных

### Таблицы (11)

#### 1. 📋 Справочные таблицы

##### `test_categories` - Категории тестов
Классификация тестов по биологическим свойствам.

| Поле | Тип | Описание |
|------|-----|----------|
| `category_id` | SERIAL PRIMARY KEY | Уникальный идентификатор категории |
| `category_name` | VARCHAR(100) NOT NULL | Название категории |
| `description` | TEXT | Подробное описание |
| `sort_order` | INTEGER | Порядок сортировки |
| `created_at` | TIMESTAMP | Дата создания |

**Данные (6 категорий):**
1. `morphological` - Морфологические свойства
2. `physiological` - Физиологические свойства  
3. `biochemical_enzymes` - Биохимические свойства - Ферменты
4. `biochemical_breakdown` - Биохимические свойства - Разложение сахаров
5. `biochemical_utilization` - Биохимические свойства - Утилизация сахаров
6. `biochemical_other` - Другие биохимические характеристики

##### `tests` - Индивидуальные тесты
Конкретные лабораторные тесты для каждой категории.

| Поле | Тип | Описание |
|------|-----|----------|
| `test_id` | SERIAL PRIMARY KEY | Уникальный идентификатор теста |
| `category_id` | INTEGER | Ссылка на категорию |
| `test_code` | VARCHAR(100) UNIQUE | Код теста |
| `test_name` | VARCHAR(200) | Название теста |
| `test_type` | VARCHAR(20) | Тип теста (boolean/numeric/text) |
| `description` | TEXT | Описание теста |
| `measurement_unit` | VARCHAR(20) | Единица измерения |
| `sort_order` | INTEGER | Порядок сортировки |
| `is_active` | BOOLEAN DEFAULT TRUE | Активность теста |

**Статистика**: 38 активных тестов

**Примеры тестов по категориям:**
- **Морфологические**: spore_formation, motility
- **Физиологические**: temperature_range, ph_range, salt_tolerance
- **Ферменты**: proteolytic_activity, catalase, oxidase, urease
- **Разложение**: starch_hydrolysis, aesculin_hydrolysis, gelatin_hydrolysis
- **Утилизация сахаров**: glucose, maltose, lactose, fructose, arabinose

##### `test_values` - Возможные значения для булевых тестов
Стандартизированные значения для интерпретации результатов.

| Поле | Тип | Описание |
|------|-----|----------|
| `value_id` | SERIAL PRIMARY KEY | Уникальный идентификатор значения |
| `test_id` | INTEGER | Ссылка на тест |
| `value_code` | VARCHAR(10) | Код значения (+, -, +/-, н.д.) |
| `value_description` | VARCHAR(100) | Описание значения |
| `sort_order` | INTEGER | Порядок сортировки |

**Стандартные значения:**
- `+` - Положительный результат
- `-` - Отрицательный результат  
- `+/-` - Вариабельный результат
- `н.д.` - Не определен

##### `data_sources` - Источники данных
Источники информации о штаммах и результатах тестов.

| Поле | Тип | Описание |
|------|-----|----------|
| `source_id` | SERIAL PRIMARY KEY | Уникальный идентификатор источника |
| `source_name` | VARCHAR(200) | Название источника |
| `source_type` | VARCHAR(50) | Тип источника |
| `description` | TEXT | Описание |
| `url` | VARCHAR(500) | URL ресурса |

##### `collection_numbers` - Номера коллекций
Номера коллекций штаммов из различных депозитариев.

| Поле | Тип | Описание |
|------|-----|----------|
| `collection_id` | SERIAL PRIMARY KEY | Уникальный идентификатор |
| `collection_name` | VARCHAR(100) | Название коллекции |
| `collection_code` | VARCHAR(20) | Код коллекции |
| `description` | TEXT | Описание коллекции |

#### 2. 🧬 Основные сущности

##### `strains` - Штаммы лизобактера
Центральная таблица с информацией о штаммах.

| Поле | Тип | Описание |
|------|-----|----------|
| `strain_id` | SERIAL PRIMARY KEY | Уникальный идентификатор штамма |
| `strain_identifier` | VARCHAR(100) UNIQUE | Уникальный код штамма |
| `scientific_name` | VARCHAR(200) | Научное название |
| `common_name` | VARCHAR(200) | Общепринятое название |
| `description` | TEXT | Описание штамма |
| `isolation_source` | TEXT | Источник выделения |
| `isolation_location` | TEXT | Место выделения |
| `isolation_date` | DATE | Дата выделения |
| `source_id` | INTEGER | Ссылка на источник данных |
| `gc_content_min` | NUMERIC(5,2) | Минимальное содержание ГЦ, % |
| `gc_content_max` | NUMERIC(5,2) | Максимальное содержание ГЦ, % |
| `gc_content_optimal` | NUMERIC(5,2) | Оптимальное содержание ГЦ, % |
| `notes` | TEXT | Примечания |
| `is_active` | BOOLEAN DEFAULT TRUE | Активность записи |
| `created_at` | TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | Дата обновления |

**Индексы:**
- Primary key на `strain_id`
- Unique на `strain_identifier`  
- B-tree на `is_active`, `source_id`
- GIN полнотекстовый поиск по идентификатору, названию, описанию

**Текущие данные:** 3 тестовых штамма (LYS-001, LYS-002, LYS-003)

##### `strain_collections` - Связь штаммов с коллекциями
Связующая таблица многие-ко-многим между штаммами и коллекциями.

| Поле | Тип | Описание |
|------|-----|----------|
| `strain_id` | INTEGER | Ссылка на штамм |
| `collection_id` | INTEGER | Ссылка на коллекцию |
| `collection_number` | VARCHAR(100) | Номер в коллекции |
| `deposit_date` | DATE | Дата депонирования |
| `notes` | TEXT | Примечания |

#### 3. 🧪 Результаты тестов

##### `test_results_boolean` - Булевы результаты
Результаты качественных тестов (+, -, +/-, н.д.).

| Поле | Тип | Описание |
|------|-----|----------|
| `result_id` | SERIAL PRIMARY KEY | Уникальный идентификатор результата |
| `strain_id` | INTEGER | Ссылка на штамм |
| `test_id` | INTEGER | Ссылка на тест |
| `value_id` | INTEGER | Ссылка на значение |
| `notes` | TEXT | Примечания к результату |
| `confidence_level` | VARCHAR(20) | Уровень достоверности |
| `tested_date` | DATE | Дата проведения теста |
| `created_at` | TIMESTAMP | Дата внесения данных |
| `updated_at` | TIMESTAMP | Дата обновления |

**Уровни достоверности:** high, medium, low

##### `test_results_numeric` - Численные результаты
Количественные результаты (температура, pH, концентрации).

| Поле | Тип | Описание |
|------|-----|----------|
| `result_id` | SERIAL PRIMARY KEY | Уникальный идентификатор результата |
| `strain_id` | INTEGER | Ссылка на штамм |
| `test_id` | INTEGER | Ссылка на тест |
| `value_type` | VARCHAR(20) | Тип значения (minimum/maximum/optimal/single) |
| `numeric_value` | NUMERIC(10,4) | Численное значение |
| `measurement_unit` | VARCHAR(20) | Единица измерения |
| `notes` | TEXT | Примечания |
| `confidence_level` | VARCHAR(20) | Уровень достоверности |
| `tested_date` | DATE | Дата проведения теста |
| `created_at` | TIMESTAMP | Дата внесения данных |
| `updated_at` | TIMESTAMP | Дата обновления |

**Типы значений:**
- `minimum` - Минимальное значение
- `maximum` - Максимальное значение
- `optimal` - Оптимальное значение
- `single` - Единичное измерение

##### `test_results_text` - Текстовые результаты
Результаты в текстовом формате (описания, комментарии).

| Поле | Тип | Описание |
|------|-----|----------|
| `result_id` | SERIAL PRIMARY KEY | Уникальный идентификатор результата |
| `strain_id` | INTEGER | Ссылка на штамм |
| `test_id` | INTEGER | Ссылка на тест |
| `text_value` | TEXT | Текстовое значение |
| `notes` | TEXT | Примечания |
| `confidence_level` | VARCHAR(20) | Уровень достоверности |
| `tested_date` | DATE | Дата проведения теста |
| `created_at` | TIMESTAMP | Дата внесения данных |
| `updated_at` | TIMESTAMP | Дата обновления |

#### 4. 📝 Аудит

##### `audit_log` - Журнал изменений
Полная история изменений всех данных в системе.

| Поле | Тип | Описание |
|------|-----|----------|
| `log_id` | SERIAL PRIMARY KEY | Уникальный идентификатор записи |
| `table_name` | VARCHAR(100) | Название таблицы |
| `record_id` | INTEGER | ID записи |
| `operation_type` | VARCHAR(10) | Тип операции (INSERT/UPDATE/DELETE) |
| `old_values` | JSONB | Старые значения |
| `new_values` | JSONB | Новые значения |
| `changed_by` | VARCHAR(100) | Пользователь |
| `changed_at` | TIMESTAMP | Время изменения |

## 📈 Представления (Views)

### `v_category_statistics` - Статистика по категориям
Сводная информация по каждой категории тестов.

**Поля:**
- `category_name` - Название категории
- `description` - Описание
- `total_tests` - Общее количество тестов
- `active_tests` - Количество активных тестов
- `strains_with_data` - Количество штаммов с данными

### `v_strains_complete` - Полная информация о штаммах
Объединенная информация о штаммах со всеми связанными данными.

### `v_test_completion` - Статистика завершенности тестов
Процент выполненных тестов для каждого штамма.

### `v_strain_completeness` - Полнота данных по штаммам
Анализ полноты данных для каждого штамма.

### `v_test_results_summary` - Сводка результатов тестов
Агрегированная информация по результатам всех тестов.

## ⚙️ Функции

### `search_strains_with_tolerance(p_criteria JSONB, p_tolerance INTEGER)`
Поиск штаммов с заданной погрешностью для численных параметров.

**Параметры:**
- `p_criteria` - JSON с критериями поиска
- `p_tolerance` - Допустимая погрешность (%)

**Возвращает:**
- `strain_id` - ID штамма
- `strain_identifier` - Идентификатор штамма
- `scientific_name` - Научное название
- `match_score` - Оценка соответствия
- `total_criteria` - Общее количество критериев
- `matching_criteria` - Количество совпадающих критериев
- `conflicting_criteria` - Количество конфликтующих критериев

### `get_strain_test_profile(p_strain_id INTEGER)`
Получение полного профиля тестов для штамма.

**Возвращает:**
- `category_name` - Название категории
- `test_name` - Название теста
- `test_type` - Тип теста
- `result_value` - Значение результата
- `confidence_level` - Уровень достоверности
- `tested_date` - Дата тестирования

### `validate_strain_data()`
Валидация целостности данных в базе.

**Возвращает:**
- `validation_type` - Тип проверки
- `strain_id` - ID штамма (если применимо)
- `strain_identifier` - Идентификатор штамма
- `issue_description` - Описание проблемы

### `bulk_import_strain_results(p_strain_identifier VARCHAR, p_test_results JSONB)`
Массовый импорт результатов тестов для штамма.

**Возвращает:** `BOOLEAN` - успех операции

### `update_updated_at_column()`
Триггерная функция для автоматического обновления поля `updated_at`.

## 🔗 Связи между таблицами

### Основные связи Foreign Key

```
strains (1) ←→ (M) test_results_boolean
strains (1) ←→ (M) test_results_numeric  
strains (1) ←→ (M) test_results_text
strains (1) ←→ (M) strain_collections
strains (M) ←→ (1) data_sources

tests (1) ←→ (M) test_results_boolean
tests (1) ←→ (M) test_results_numeric
tests (1) ←→ (M) test_results_text
tests (M) ←→ (1) test_categories
tests (1) ←→ (M) test_values

strain_collections (M) ←→ (1) collection_numbers
test_results_boolean (M) ←→ (1) test_values
```

### Каскадные удаления

При удалении штамма автоматически удаляются:
- Все результаты тестов (boolean, numeric, text)
- Связи с коллекциями

## 📋 Индексы для производительности

### B-tree индексы
- `strains.strain_identifier` (UNIQUE)
- `strains.is_active`
- `strains.source_id`
- `tests.test_code` (UNIQUE)
- `tests.category_id`
- `test_results_*.strain_id`
- `test_results_*.test_id`

### GIN индексы
- `strains` - полнотекстовый поиск по идентификатору, названию, описанию

### Составные индексы
- `test_results_boolean (strain_id, test_id)`
- `test_results_numeric (strain_id, test_id, value_type)`

## 🔄 Триггеры

### `update_strains_updated_at`
Автоматически обновляет поле `updated_at` при изменении записи в таблице `strains`.

### Аудит триггеры (планируются)
- Автоматическое логирование изменений в `audit_log`
- Контроль целостности данных

## 📊 Текущая статистика

```sql
-- Основные данные
Штаммы: 3 (тестовые)
Категории тестов: 6
Активные тесты: 38
Булевы результаты: 0 (в процессе загрузки)
Численные результаты: 0 (в процессе загрузки)  
Текстовые результаты: 0 (в процессе загрузки)
```

## 🚀 Производительность

### Оптимизации
- Использование SERIAL для автоинкремента
- Индексы на часто используемые поля
- Полнотекстовый поиск с GIN индексом
- Каскадные операции для целостности
- Триггеры для автоматизации

### Рекомендации по использованию
- Используйте представления для сложных запросов
- Применяйте функции поиска для фильтрации штаммов
- Регулярно обновляйте статистику PostgreSQL
- Мониторьте производительность индексов

## 🔧 Команды для работы

```bash
# Подключение к базе
make -f Makefile.docker docker-shell

# Статистика
make -f Makefile.docker stats

# Проверка структуры
\dt lysobacter.*    # Таблицы
\dv lysobacter.*    # Представления  
\df lysobacter.*    # Функции

# Примеры запросов
SELECT * FROM lysobacter.v_category_statistics;
SELECT * FROM lysobacter.get_strain_test_profile(1);
```

---

**Структура базы данных полностью соответствует требованиям 3NF и готова для продуктивного использования в исследованиях штаммов лизобактера.** 