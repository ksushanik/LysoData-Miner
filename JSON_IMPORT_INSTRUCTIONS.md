# ИНСТРУКЦИИ ПО ИМПОРТУ JSON ДАННЫХ ШТАММОВ ЛИЗОБАКТЕРИЙ

## ✅ ПРЕИМУЩЕСТВА JSON ФОРМАТА

JSON формат имеет множество преимуществ по сравнению с Excel:

- 🚀 **Простота для LLM**: JSON является естественным форматом вывода для языковых моделей
- ✅ **Автоматическая валидация**: Структура данных проверяется автоматически
- 🔧 **Нет проблем с ячейками**: Отсутствуют проблемы форматирования Excel
- 🌐 **Универсальность**: Поддерживается всеми современными системами
- 📊 **Вложенные данные**: Идеально подходит для связанных данных штаммов и тестов

## 🎯 WORKFLOW ИСПОЛЬЗОВАНИЯ

### 1. ПОЛУЧЕНИЕ ДАННЫХ ОТ LLM

Используйте промпт из файла `LLM_JSON_STRUCTURING_PROMPT.md`:

```bash
# Скопируйте содержимое промпта и отправьте LLM вместе с вашими данными
cat LLM_JSON_STRUCTURING_PROMPT.md
```

LLM вернёт JSON в таком формате:
```json
{
  "metadata": {
    "source": "Research paper: Smith et al. 2023",
    "created_date": "2025-06-26",
    "total_strains": 3,
    "total_test_results": 12
  },
  "strains": [
    {
      "strain_identifier": "LYS-001",
      "scientific_name": "Lysobacter enzymogenes",
      "test_results": [
        {
          "test_code": "spore_formation",
          "result_value": "-",
          "test_type": "boolean",
          "confidence_level": "high"
        }
      ]
    }
  ]
}
```

### 2. СОХРАНЕНИЕ JSON ФАЙЛА

```bash
# Сохраните полученный JSON в файл
nano my_strains_data.json

# Или скачайте от LLM и поместите в директорию проекта
```

### 3. ЗАПУСК БАЗЫ ДАННЫХ

```bash
# Запустите PostgreSQL в Docker
make start

# Проверьте статус
make status
```

### 4. ВАЛИДАЦИЯ JSON (РЕКОМЕНДУЕТСЯ!)

```bash
# Сначала проверьте структуру JSON
make validate-json JSON_FILE=my_strains_data.json
```

Возможные ошибки валидации:
- ❌ Неправильные коды тестов
- ❌ Недопустимые булевые значения  
- ❌ Неправильные форматы дат
- ❌ Отсутствующие обязательные поля

### 5. ИМПОРТ ДАННЫХ

```bash
# Импортируйте данные в базу
make import-json JSON_FILE=my_strains_data.json
```

Успешный импорт покажет:
```
✓ JSON structure validation passed
✓ Imported strain: LYS-001 (ID: 1)
✓ Imported strain: LYS-002 (ID: 2)
✓ Successfully imported 2 strains and 8 test results
```

### 6. ПРОВЕРКА РЕЗУЛЬТАТОВ

```bash
# Проверьте статистику базы
make stats

# Найдите конкретный штамм
make search-strain STRAIN_ID=LYS-001
```

## 🔧 КОМАНДЫ УПРАВЛЕНИЯ

### Основные команды JSON импорта:

```bash
# Создать шаблон JSON для примера
make generate-json-template

# Валидировать структуру JSON
make validate-json JSON_FILE=filename.json

# Импортировать данные из JSON  
make import-json JSON_FILE=filename.json

# Универсальная команда (автоопределение формата)
make import-data FILE=filename.json
make import-data FILE=filename.xlsx
```

### Команды управления базой данных:

```bash
# Запуск/остановка системы
make start          # Запустить базу данных
make start-admin    # Запустить с web-интерфейсом pgAdmin
make stop           # Остановить систему
make restart        # Перезапустить систему

# Мониторинг и статистика
make status         # Статус системы
make stats          # Статистика данных
make show-strains   # Список всех штаммов
make show-categories # Категории тестов

# Резервное копирование
make backup         # Создать backup
make backup-list    # Список backup'ов
make restore BACKUP_FILE=filename.sql.gz
```

## 📋 ТРЕБОВАНИЯ К JSON СТРУКТУРЕ

### Обязательные поля верхнего уровня:
- `metadata` - метаданные файла
- `strains` - массив штаммов

### Обязательные поля штамма:
- `strain_identifier` - уникальный идентификатор

### Обязательные поля теста:
- `test_code` - код теста из разрешенного списка
- `result_value` - значение результата
- `test_type` - тип теста: "boolean", "numeric", "text"

### Точные коды тестов:

**Морфологические:**
- `spore_formation`, `motility`

**Физиологические:**
- `temperature`, `ph_level`, `salt_tolerance`

**Биохимические (ферменты):**
- `proteolytic_activity`, `oxidase`, `catalase`, `urease`, `nitrate_reduction`, `indole_production`, `phosphatase`, `esterase`

**Биохимические (разложение):**
- `starch`, `aesculin`, `gelatin`, `casein`, `tween_20`, `tween_40`, `tween_60`, `chitin`, `cellulose`, `arginine_hydrolase`, `pectin`, `glucose_fermentation`

**Биохимические (утилизация сахаров):**
- `maltose`, `lactose`, `fructose`, `arabinose`, `mannose`, `trehalose`, `sorbitol`, `mannitol`, `dextrose`, `xylose`, `galactose`, `dulcitol`, `cellobiose`, `sucrose`, `raffinose`, `inositol`

**Другие:**
- `cellulase_activity`, `phosphate_solubilization`, `gc_content`

### Допустимые значения:

**Булевые тесты:** ТОЛЬКО `"+"`, `"-"`, `"+/-"`, `"n.d."`

**Числовые тесты:** Числовые значения как строки: `"25"`, `"7.2"`, `"15.5"`

**value_type для числовых:** `"minimum"`, `"maximum"`, `"optimal"`, `"single"`

**confidence_level:** `"high"`, `"medium"`, `"low"`

**Даты:** Только формат `"YYYY-MM-DD"`

## ⚠️ ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

### ❌ Неправильные коды тестов
```json
// НЕПРАВИЛЬНО:
"test_code": "spore"
"test_code": "motile"

// ПРАВИЛЬНО:
"test_code": "spore_formation"
"test_code": "motility"
```

### ❌ Неправильные булевые значения
```json
// НЕПРАВИЛЬНО:
"result_value": "positive"
"result_value": "+"
"result_value": 1

// ПРАВИЛЬНО:
"result_value": "+"
"result_value": "-"
"result_value": "+/-"
"result_value": "n.d."
```

### ❌ Неправильные числовые значения
```json
// НЕПРАВИЛЬНО:
"result_value": 25
"result_value": "25°C"

// ПРАВИЛЬНО:
"result_value": "25"
"measurement_unit": "°C"
```

### ❌ Неправильные даты
```json
// НЕПРАВИЛЬНО:
"isolation_date": "01/15/2023"
"tested_date": "15.01.2023"

// ПРАВИЛЬНО:
"isolation_date": "2023-01-15"
"tested_date": "2023-01-15"
```

## 🎯 РЕКОМЕНДАЦИИ

1. **Всегда валидируйте** JSON перед импортом: `make validate-json`
2. **Создавайте backup** перед импортом: `make backup`
3. **Проверяйте коды тестов** - используйте точно те, что указаны в промпте
4. **Используйте шаблон** для понимания структуры: `make generate-json-template`
5. **Проверяйте результаты** после импорта: `make stats`

## 📞 ПОДДЕРЖКА

При проблемах:

1. Проверьте логи: `make logs`
2. Проверьте соединение: `make test-connection`
3. Посмотрите статус: `make status`
4. Проверьте валидацию: `make validate-json`

**Система готова к продуктивному использованию с JSON данными от LLM!** 