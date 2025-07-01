# ПРОМПТ ДЛЯ LLM: СТРУКТУРИРОВАНИЕ ДАННЫХ ШТАММОВ ЛИЗОБАКТЕРИЙ

## ЗАДАЧА
Ты - эксперт по структурированию микробиологических данных. Тебе нужно преобразовать неструктурированные данные о штаммах лизобактерий в точно определенный формат Excel для импорта в базу данных PostgreSQL.

## ВАЖНО: СТРОГИЕ ТРЕБОВАНИЯ К ФОРМАТУ

### 1. СТРУКТУРА EXCEL ФАЙЛА
Создай Excel файл с **ДВУМЯ ОБЯЗАТЕЛЬНЫМИ ЛИСТАМИ**:

#### ЛИСТ 1: "Strains" (Информация о штаммах)
**ОБЯЗАТЕЛЬНЫЕ КОЛОНКИ:**
- `strain_identifier` (STRING, УНИКАЛЬНЫЙ) - Основной идентификатор штамма (например: "LYS-001", "ATCC-123")
- `scientific_name` (STRING) - Научное название (например: "Lysobacter enzymogenes")
- `common_name` (STRING) - Обычное название или альтернативное обозначение
- `description` (TEXT) - Детальное описание штамма
- `isolation_source` (STRING) - Источник выделения (почва, растение, вода и т.д.)
- `isolation_location` (STRING) - Географическое место выделения
- `isolation_date` (DATE в формате YYYY-MM-DD) - Дата выделения
- `notes` (TEXT) - Дополнительные заметки

**ПРИМЕР СТРОКИ:**
```
strain_identifier: LYS-001
scientific_name: Lysobacter enzymogenes
common_name: Strain C3
description: Highly active biocontrol strain isolated from rhizosphere
isolation_source: Rhizosphere soil
isolation_location: Agricultural field, Germany
isolation_date: 2023-05-15
notes: Shows strong antifungal activity against plant pathogens
```

#### ЛИСТ 2: "TestResults" (Результаты тестов)
**ОБЯЗАТЕЛЬНЫЕ КОЛОНКИ:**
- `strain_identifier` (STRING) - Связь со штаммом из листа "Strains"
- `test_code` (STRING) - Код теста из списка разрешенных (см. ниже)
- `result_value` (STRING/NUMERIC) - Значение результата теста
- `value_type` (STRING) - Для числовых тестов: "minimum", "maximum", "optimal", "single"
- `measurement_unit` (STRING) - Единица измерения для числовых тестов
- `confidence_level` (STRING) - "high", "medium", "low"
- `tested_date` (DATE в формате YYYY-MM-DD) - Дата проведения теста
- `notes` (TEXT) - Комментарии к результату

## 2. ТОЧНЫЕ КОДЫ ТЕСТОВ И ЗНАЧЕНИЯ

### МОРФОЛОГИЧЕСКИЕ ТЕСТЫ (morphological)
- `motility` - Значения: "+", "-", "+/-", "n.d."
(NOTE: spore_formation removed - all Lysobacter are non-spore-forming gram-negative rods)

### ФИЗИОЛОГИЧЕСКИЕ ТЕСТЫ (physiological)
- `temperature` - Числовые значения в °C (указать value_type)
- `ph_level` - Числовые значения pH (указать value_type)
- `salt_tolerance` - Значения: "+", "-", "+/-", "n.d."

### БИОХИМИЧЕСКИЕ ТЕСТЫ - ФЕРМЕНТЫ (biochemical_enzymes)
- `proteolytic_activity` - Значения: "+", "-", "+/-", "n.d."
- `oxidase` - Значения: "+", "-", "+/-", "n.d."
- `catalase` - Значения: "+", "-", "+/-", "n.d."
- `urease` - Значения: "+", "-", "+/-", "n.d."
- `nitrate_reduction` - Значения: "+", "-", "+/-", "n.d."
- `indole_production` - Значения: "+", "-", "+/-", "n.d."
- `phosphatase` - Значения: "+", "-", "+/-", "n.d."
- `esterase` - Значения: "+", "-", "+/-", "n.d."

### БИОХИМИЧЕСКИЕ ТЕСТЫ - РАЗЛОЖЕНИЕ (biochemical_breakdown)
- `starch` - Значения: "+", "-", "+/-", "n.d."
- `aesculin` - Значения: "+", "-", "+/-", "n.d."
- `gelatin` - Значения: "+", "-", "+/-", "n.d."
- `casein` - Значения: "+", "-", "+/-", "n.d."
- `tween_20` - Значения: "+", "-", "+/-", "n.d."
- `tween_40` - Значения: "+", "-", "+/-", "n.d."
- `tween_60` - Значения: "+", "-", "+/-", "n.d."
- `chitin` - Значения: "+", "-", "+/-", "n.d."
- `cellulose` - Значения: "+", "-", "+/-", "n.d."
- `arginine_hydrolase` - Значения: "+", "-", "+/-", "n.d."
- `pectin` - Значения: "+", "-", "+/-", "n.d."
- `glucose_fermentation` - Значения: "+", "-", "+/-", "n.d."

### БИОХИМИЧЕСКИЕ ТЕСТЫ - УТИЛИЗАЦИЯ САХАРОВ (biochemical_utilization)
- `maltose` - Значения: "+", "-", "+/-", "n.d."
- `lactose` - Значения: "+", "-", "+/-", "n.d."
- `fructose` - Значения: "+", "-", "+/-", "n.d."
- `arabinose` - Значения: "+", "-", "+/-", "n.d."
- `mannose` - Значения: "+", "-", "+/-", "n.d."
- `trehalose` - Значения: "+", "-", "+/-", "n.d."
- `sorbitol` - Значения: "+", "-", "+/-", "n.d."
- `mannitol` - Значения: "+", "-", "+/-", "n.d."
- `dextrose` - Значения: "+", "-", "+/-", "n.d."
- `xylose` - Значения: "+", "-", "+/-", "n.d."
- `galactose` - Значения: "+", "-", "+/-", "n.d."
- `dulcitol` - Значения: "+", "-", "+/-", "n.d."
- `cellobiose` - Значения: "+", "-", "+/-", "n.d."
- `sucrose` - Значения: "+", "-", "+/-", "n.d."
- `raffinose` - Значения: "+", "-", "+/-", "n.d."
- `inositol` - Значения: "+", "-", "+/-", "n.d."

### ДРУГИЕ БИОХИМИЧЕСКИЕ ТЕСТЫ (biochemical_other)
- `cellulase_activity` - Значения: "+", "-", "+/-", "n.d."
- `phosphate_solubilization` - Значения: "+", "-", "+/-", "n.d."
- `gc_content` - Числовые значения в % (указать value_type)

## 3. ПРИМЕРЫ ПРАВИЛЬНЫХ ЗАПИСЕЙ

### Пример булевого теста:
```
strain_identifier: LYS-001
test_code: catalase
result_value: +
value_type: (пустое)
measurement_unit: (пустое)
confidence_level: high
tested_date: 2023-06-01
notes: Strong positive reaction
```

### Пример числового теста:
```
strain_identifier: LYS-001
test_code: temperature
result_value: 25
value_type: optimal
measurement_unit: °C
confidence_level: high
tested_date: 2023-06-01
notes: Optimal growth temperature
```

### Дополнительные записи для диапазона:
```
strain_identifier: LYS-001
test_code: temperature
result_value: 15
value_type: minimum
measurement_unit: °C
confidence_level: high
tested_date: 2023-06-01
notes: Minimum growth temperature

strain_identifier: LYS-001
test_code: temperature
result_value: 35
value_type: maximum
measurement_unit: °C
confidence_level: high
tested_date: 2023-06-01
notes: Maximum growth temperature
```

## 4. ПРАВИЛА ВАЛИДАЦИИ

### КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
1. **strain_identifier** должен быть УНИКАЛЬНЫМ для каждого штамма
2. **test_code** должен точно соответствовать списку выше (регистр важен)
3. **result_value** для булевых тестов: ТОЛЬКО "+", "-", "+/-", "n.d."
4. **result_value** для числовых тестов: только числа (целые или десятичные)
5. **value_type** обязателен для числовых тестов
6. **Даты** только в формате YYYY-MM-DD
7. **confidence_level** только: "high", "medium", "low"

### ОБРАБОТКА НЕОПРЕДЕЛЕННОСТИ:
- Если данные отсутствуют: используй "n.d." для булевых тестов
- Если данные неточные: используй "+/-" для булевых тестов
- Если уверенность низкая: укажи confidence_level: "low"

## 5. ИНСТРУКЦИИ ПО ИЗВЛЕЧЕНИЮ ДАННЫХ

### ИЗ НАУЧНЫХ СТАТЕЙ:
1. Ищи таблицы с характеристиками штаммов
2. Ищи разделы "Materials and Methods" для условий тестирования
3. Обращай внимание на сокращения и обозначения
4. Проверяй единицы измерения

### ИЗ ОПИСАНИЙ ШТАММОВ:
1. strain_identifier обычно указан в начале описания
2. Научные названия часто выделены курсивом
3. Источники выделения описаны в разделе "isolation"
4. Географические данные ищи в "origin" или "locality"

### ВАЖНЫЕ ЗАМЕЧАНИЯ:
- При сомнениях лучше указать "n.d." чем неточные данные
- Всегда указывай источник в notes если известен
- Сохраняй оригинальные обозначения в notes
- Проверяй соответствие test_code нашему списку

## 6. ФОРМАТ ОТВЕТА

Создай Excel файл с двумя листами и предоставь:
1. Сам Excel файл
2. Сводку: количество штаммов и тестов
3. Список проблем или неопределенностей
4. Рекомендации по дополнительной проверке данных

**РЕЗУЛЬТАТ ДОЛЖЕН БЫТЬ ГОТОВ ДЛЯ ПРЯМОГО ИМПОРТА В БАЗУ ДАННЫХ БЕЗ ДОПОЛНИТЕЛЬНОЙ ОБРАБОТКИ!** 