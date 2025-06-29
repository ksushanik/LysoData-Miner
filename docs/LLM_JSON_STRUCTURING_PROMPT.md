# ПРОМПТ ДЛЯ LLM: СТРУКТУРИРОВАНИЕ ДАННЫХ ШТАММОВ ЛИЗОБАКТЕРИЙ В JSON

## ЗАДАЧА
Ты - эксперт по структурированию микробиологических данных. Тебе нужно преобразовать неструктурированные данные о штаммах лизобактерий в точно определенный JSON формат для автоматического импорта в базу данных PostgreSQL.

## ВАЖНО: JSON ФОРМАТ НАМНОГО ПРОЩЕ ДЛЯ LLM!

JSON формат имеет следующие преимущества:
- ✅ Естественный для LLM формат вывода
- ✅ Автоматическая валидация структуры
- ✅ Простота обработки вложенных данных
- ✅ Нет проблем с Excel ячейками и листами
- ✅ Прямая интеграция с API

## 1. СТРУКТУРА JSON ФАЙЛА

```json
{
  "metadata": {
    "source": "название источника данных",
    "created_date": "YYYY-MM-DD",
    "total_strains": 0,
    "total_test_results": 0,
    "notes": "дополнительные комментарии"
  },
  "strains": [
    {
      "strain_identifier": "уникальный идентификатор",
      "scientific_name": "научное название",
      "common_name": "обычное название",
      "description": "описание штамма",
      "isolation_source": "источник выделения",
      "isolation_location": "место выделения",
      "isolation_date": "YYYY-MM-DD",
      "notes": "заметки",
      "test_results": [
        {
          "test_code": "код_теста",
          "result_value": "значение_результата",
          "test_type": "boolean|numeric|text",
          "value_type": "minimum|maximum|optimal|single",
          "measurement_unit": "единица_измерения",
          "confidence_level": "high|medium|low",
          "tested_date": "YYYY-MM-DD",
          "notes": "комментарии к тесту"
        }
      ]
    }
  ]
}
```

## 2. ТОЧНЫЕ КОДЫ ТЕСТОВ (КОПИРУЙ БЕЗ ИЗМЕНЕНИЙ!)

### МОРФОЛОГИЧЕСКИЕ ТЕСТЫ
- `spore_formation` - Значения: "+", "-", "+/-", "n.d."
- `motility` - Значения: "+", "-", "+/-", "n.d."

### ФИЗИОЛОГИЧЕСКИЕ ТЕСТЫ  
- `temperature` - Числовые значения в °C
- `ph_level` - Числовые значения pH
- `salt_tolerance` - Значения: "+", "-", "+/-", "n.d."

### БИОХИМИЧЕСКИЕ ТЕСТЫ - ФЕРМЕНТЫ
- `proteolytic_activity` - Значения: "+", "-", "+/-", "n.d."
- `oxidase` - Значения: "+", "-", "+/-", "n.d."
- `catalase` - Значения: "+", "-", "+/-", "n.d."
- `urease` - Значения: "+", "-", "+/-", "n.d."
- `nitrate_reduction` - Значения: "+", "-", "+/-", "n.d."
- `indole_production` - Значения: "+", "-", "+/-", "n.d."
- `phosphatase` - Значения: "+", "-", "+/-", "n.d."
- `esterase` - Значения: "+", "-", "+/-", "n.d."

### БИОХИМИЧЕСКИЕ ТЕСТЫ - РАЗЛОЖЕНИЕ
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

### БИОХИМИЧЕСКИЕ ТЕСТЫ - УТИЛИЗАЦИЯ САХАРОВ
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

### ДРУГИЕ БИОХИМИЧЕСКИЕ ТЕСТЫ
- `cellulase_activity` - Значения: "+", "-", "+/-", "n.d."
- `phosphate_solubilization` - Значения: "+", "-", "+/-", "n.d."
- `gc_content` - Числовые значения в %

## 3. ПРИМЕР ПРАВИЛЬНОГО JSON

```json
{
  "metadata": {
    "source": "Research paper: Jones et al. 2023",
    "created_date": "2025-06-26",
    "total_strains": 2,
    "total_test_results": 8,
    "notes": "Data extracted from Table 2 and supplementary materials"
  },
  "strains": [
    {
      "strain_identifier": "LYS-001",
      "scientific_name": "Lysobacter enzymogenes",
      "common_name": "Strain C3",
      "description": "Highly active biocontrol strain isolated from rhizosphere",
      "isolation_source": "Rhizosphere soil",
      "isolation_location": "Agricultural field, Germany", 
      "isolation_date": "2023-05-15",
      "notes": "Shows strong antifungal activity",
      "test_results": [
        {
          "test_code": "spore_formation",
          "result_value": "-",
          "test_type": "boolean",
          "value_type": null,
          "measurement_unit": null,
          "confidence_level": "high",
          "tested_date": "2023-06-01",
          "notes": "No spores observed under microscope"
        },
        {
          "test_code": "motility", 
          "result_value": "+",
          "test_type": "boolean",
          "value_type": null,
          "measurement_unit": null,
          "confidence_level": "high",
          "tested_date": "2023-06-01",
          "notes": "Strong motility observed"
        },
        {
          "test_code": "temperature",
          "result_value": "15",
          "test_type": "numeric",
          "value_type": "minimum",
          "measurement_unit": "°C",
          "confidence_level": "high",
          "tested_date": "2023-06-02",
          "notes": "Minimum growth temperature"
        },
        {
          "test_code": "temperature",
          "result_value": "35",
          "test_type": "numeric", 
          "value_type": "maximum",
          "measurement_unit": "°C",
          "confidence_level": "high",
          "tested_date": "2023-06-02",
          "notes": "Maximum growth temperature"
        },
        {
          "test_code": "temperature",
          "result_value": "25",
          "test_type": "numeric",
          "value_type": "optimal", 
          "measurement_unit": "°C",
          "confidence_level": "high",
          "tested_date": "2023-06-02",
          "notes": "Optimal growth temperature"
        },
        {
          "test_code": "catalase",
          "result_value": "+",
          "test_type": "boolean",
          "value_type": null,
          "measurement_unit": null,
          "confidence_level": "high",
          "tested_date": "2023-06-03",
          "notes": "Strong positive reaction"
        }
      ]
    },
    {
      "strain_identifier": "LYS-002",
      "scientific_name": "Lysobacter antibioticus",
      "common_name": "Biocontrol strain B",
      "description": "Antibiotic-producing strain",
      "isolation_source": "Agricultural soil",
      "isolation_location": "Netherlands",
      "isolation_date": "2023-06-20",
      "notes": "Produces multiple bioactive compounds",
      "test_results": [
        {
          "test_code": "spore_formation",
          "result_value": "+",
          "test_type": "boolean", 
          "value_type": null,
          "measurement_unit": null,
          "confidence_level": "high",
          "tested_date": "2023-06-10",
          "notes": "Spore formation observed"
        },
        {
          "test_code": "catalase",
          "result_value": "+",
          "test_type": "boolean",
          "value_type": null,
          "measurement_unit": null,
          "confidence_level": "high", 
          "tested_date": "2023-06-11",
          "notes": "Positive catalase test"
        }
      ]
    }
  ]
}
```

## 4. СТРОГИЕ ПРАВИЛА ВАЛИДАЦИИ

### КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
1. **strain_identifier** - уникальный для каждого штамма
2. **test_code** - точно из списка выше (без изменений!)
3. **result_value** для булевых: ТОЛЬКО "+", "-", "+/-", "n.d."
4. **result_value** для числовых: только числа (15, 25.5, 7.2)
5. **test_type** - точно: "boolean", "numeric", "text"
6. **value_type** - для числовых: "minimum", "maximum", "optimal", "single"
7. **confidence_level** - точно: "high", "medium", "low"
8. **Даты** - только YYYY-MM-DD формат
9. **measurement_unit** - для числовых тестов: "°C", "pH", "%"

### ДЛЯ БУЛЕВЫХ ТЕСТОВ:
```json
{
  "test_code": "catalase",
  "result_value": "+",
  "test_type": "boolean", 
  "value_type": null,
  "measurement_unit": null
}
```

### ДЛЯ ЧИСЛОВЫХ ТЕСТОВ:
```json
{
  "test_code": "temperature",
  "result_value": "25",
  "test_type": "numeric",
  "value_type": "optimal",
  "measurement_unit": "°C"
}
```

## 5. ОБРАБОТКА НЕОПРЕДЕЛЕННОСТИ

### Если данные отсутствуют:
- Булевые тесты: `"result_value": "n.d."`
- Поля могут быть: `null` или не включены

### Если данные неточные:
- Булевые тесты: `"result_value": "+/-"`
- Низкая уверенность: `"confidence_level": "low"`

### Если диапазон неизвестен:
- Одно значение: `"value_type": "single"`

## 6. ИНСТРУКЦИИ ПО ИЗВЛЕЧЕНИЮ

### ИЗ НАУЧНЫХ СТАТЕЙ:
1. Ищи таблицы характеристик штаммов
2. Внимательно читай единицы измерения
3. Проверяй сокращения и символы
4. Смотри разделы Materials and Methods

### ИЗ ОПИСАНИЙ:
1. strain_identifier обычно в начале
2. Научные названия курсивом
3. Источники в разделе isolation
4. Места в origin/locality

## 7. ФИНАЛЬНАЯ ПРОВЕРКА

Перед выводом JSON:
- ✅ Все test_code из разрешенного списка
- ✅ Все булевые значения: "+", "-", "+/-", "n.d."
- ✅ Все числовые значения - только числа
- ✅ Все даты в формате YYYY-MM-DD
- ✅ JSON синтаксически корректен
- ✅ metadata заполнен

## 8. ФОРМАТ ОТВЕТА

Верни ТОЛЬКО валидный JSON без дополнительного текста:

```json
{
  "metadata": { ... },
  "strains": [ ... ]
}
```

**ГОТОВО ДЛЯ ПРЯМОГО ИМПОРТА В БАЗУ ДАННЫХ!** 