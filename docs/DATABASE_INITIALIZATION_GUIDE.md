# База данных Lysobacter - Руководство по инициализации

## 🎯 Обзор системы

Система базы данных Lysobacter настроена для **гарантированной инициализации** с правильной структурой при любом сценарии развертывания. База данных содержит:

- **6 категорий тестов**
- **43 теста** (spore_formation removed - all Lysobacter are non-spore-forming)
- **Нормализованная структура 3NF**
- **Автоматическая валидация**

## 📊 Структура базы данных

### Категории тестов (6)
1. **morphological** (1 тест) - Морфологические свойства
2. **physiological** (3 теста) - Физиологические свойства  
3. **biochemical_enzymes** (10 тестов) - Биохимические ферменты
4. **biochemical_breakdown** (12 тестов) - Разложение полисахаридов
5. **biochemical_utilization** (16 тестов) - Утилизация сахаров
6. **biochemical_other** (1 тест) - Прочие биохимические свойства

### Полный список тестов (44)

#### Морфологические (1)
- `motility` - Подвижность
(NOTE: spore_formation removed - all Lysobacter are non-spore-forming gram-negative rods)

#### Физиологические (3)
- `temperature` - Температурный диапазон (numeric)
- `ph_level` - pH диапазон (numeric)
- `salt_tolerance` - Солеустойчивость (boolean)

#### Биохимические ферменты (10)
- `proteolytic_activity` - Протеолитическая активность
- `oxidase` - Оксидаза
- `catalase` - Каталаза
- `urease` - Уреаза
- `nitrate_reduction` - Восстановление нитратов
- `indole_production` - Образование индола
- `phosphatase` - Фосфатаза
- `esterase` - Эстераза
- `cellulase_activity` - Целлюлазная активность
- `phosphate_solubilization` - Солюбилизация фосфатов

#### Биохимическое разложение (12)
- `starch` - Разложение крахмала
- `aesculin` - Разложение эскулина
- `gelatin` - Разложение желатина
- `casein` - Разложение казеина
- `tween_20` - Разложение Tween 20
- `tween_40` - Разложение Tween 40
- `tween_60` - Разложение Tween 60
- `chitin` - Разложение хитина
- `cellulose` - Разложение целлюлозы
- `arginine_hydrolase` - Аргинин гидролаза
- `pectin` - Разложение пектина
- `glucose_fermentation` - Ферментация глюкозы

#### Биохимическая утилизация (16)
- `maltose` - Утилизация мальтозы
- `lactose` - Утилизация лактозы
- `fructose` - Утилизация фруктозы
- `arabinose` - Утилизация арабинозы
- `mannose` - Утилизация маннозы
- `trehalose` - Утилизация трегалозы
- `sorbitol` - Утилизация сорбитола
- `mannitol` - Утилизация маннитола
- `dextrose` - Утилизация декстрозы
- `xylose` - Утилизация ксилозы
- `galactose` - Утилизация галактозы
- `dulcitol` - Утилизация дульцитола
- `cellobiose` - Утилизация целлобиозы
- `sucrose` - Утилизация сахарозы
- `raffinose` - Утилизация рафинозы
- `inositol` - Утилизация инозитола

#### Прочие биохимические (1)
- `gc_content` - Содержание GC (numeric)

## 🔧 Команды управления

### Основные команды
```bash
# Запуск системы
make start

# Статистика базы данных
make stats

# Просмотр категорий
make show-categories

# Полная переинициализация (с подтверждением)
make full-reset

# Очистка данных (сохранение справочников)
make clean-data
```

### Импорт данных
```bash
# Генерация шаблона JSON
make generate-json-template

# Валидация JSON файла
make validate-json JSON_FILE=file.json

# Импорт JSON данных
make import-json JSON_FILE=file.json
```

## 🚀 Сценарии инициализации

### 1. Новая установка
```bash
git clone [repository]
cd lysobacters
make start
# Автоматически создается база с 44 тестами
```

### 2. Восстановление после сбоя
```bash
make full-reset
# Введите 'yes' для подтверждения
# Система полностью переинициализируется
```

### 3. Обновление структуры
```bash
make stop
docker volume rm lysobacters_postgres_data
make start
# База пересоздается с актуальной структурой
```

### 4. Очистка для продакшн данных
```bash
make clean-data
# Удаляются только тестовые данные
# Справочники остаются
```

## 📁 Ключевые файлы инициализации

### database/schema/01_create_tables.sql
- Создание всех таблиц
- Индексы и ограничения
- Триггеры для аудита

### database/schema/02_insert_reference_data.sql
- **6 категорий тестов**
- **44 теста** с правильными типами
- Стандартные значения для булевых тестов
- Примеры источников данных

### database/schema/03_views_and_functions.sql
- Представления для удобного доступа
- Функции поиска и валидации

## ✅ Проверка правильности инициализации

После любой инициализации проверьте:

```bash
make stats
```

**Ожидаемый результат:**
```
Test Categories | 6
Tests           | 44
Strains         | 0 (после clean-data)
Boolean Results | 0 (после clean-data)
Numeric Results | 0 (после clean-data)
Text Results    | 0 (после clean-data)
```

```bash
make show-categories
```

**Ожидаемый результат:**
```
morphological           | 2
physiological           | 3  
biochemical_enzymes     | 10
biochemical_breakdown   | 12
biochemical_utilization | 16
biochemical_other       | 1
```

## 🎯 Workflow для реальных данных

1. **Подготовка системы:**
   ```bash
   make start
   make clean-data  # Очистить тестовые данные
   ```

2. **Импорт данных:**
   ```bash
   make validate-json JSON_FILE=your_data.json
   make import-json JSON_FILE=your_data.json
   ```

3. **Проверка:**
   ```bash
   make stats
   ```

## 🔒 Гарантии системы

### ✅ Что гарантировано:
- **44 теста** в **6 категориях** при каждой инициализации
- Полное соответствие промпту LLM_JSON_STRUCTURING_PROMPT.md
- Нормализованная структура 3NF
- Корректные типы данных и ограничения
- Автоматическая валидация JSON

### ✅ Безопасность:
- Подтверждение опасных операций
- Backup справочных данных при очистке
- Проверка целостности при импорте
- Автоматическая валидация структуры

### ✅ Совместимость:
- Docker контейнеры на любой ОС
- PostgreSQL 15+ с расширениями
- Поддержка восстановления из backup
- Масштабируемая архитектура

## 📞 Поддержка

При проблемах с инициализацией:

1. Проверьте логи: `docker-compose logs postgres`
2. Выполните полный сброс: `make full-reset`
3. Проверьте статистику: `make stats`
4. Сравните с ожидаемыми значениями выше

**Система обеспечивает стабильную и предсказуемую инициализацию базы данных для штаммов Lysobacter.** 