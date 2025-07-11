# ИНСТРУКЦИИ ПО ИМПОРТУ СТРУКТУРИРОВАННЫХ ДАННЫХ

## ПОСЛЕ ПОЛУЧЕНИЯ EXCEL ФАЙЛА ОТ LLM

### 1. ПРОВЕРКА ФОРМАТА
Убедитесь, что Excel файл содержит:
- ✅ Лист "Strains" с 8 обязательными колонками
- ✅ Лист "TestResults" с 8 обязательными колонками  
- ✅ Все значения test_code соответствуют разрешенным кодам
- ✅ Булевые значения только: "+", "-", "+/-", "n.d."
- ✅ Даты в формате YYYY-MM-DD
- ✅ Числовые значения для числовых тестов

### 2. ЗАПУСК БАЗЫ ДАННЫХ
```bash
# Запуск PostgreSQL в Docker
make start

# Проверка статуса
make status
```

### 3. ИМПОРТ ДАННЫХ

#### Полный импорт (штаммы + результаты тестов):
```bash
make import-excel-all EXCEL_FILE=путь_к_файлу.xlsx
```

#### Импорт только штаммов:
```bash
make import-excel-strains EXCEL_FILE=путь_к_файлу.xlsx
```

#### Импорт только результатов тестов:
```bash
make import-excel-results EXCEL_FILE=путь_к_файлу.xlsx
```

### 4. ПРОВЕРКА ИМПОРТА

#### Статистика базы данных:
```bash
make stats
```

#### Проверка конкретного штамма:
```bash
make search-strain STRAIN_ID=LYS-001
```

#### Валидация целостности данных:
```bash
make validate-data
```

### 5. ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

#### Ошибка: "Test code not found"
**Проблема:** test_code не соответствует разрешенным значениям
**Решение:** Проверьте список кодов в LLM_DATA_STRUCTURING_PROMPT.md

#### Ошибка: "Invalid boolean value"
**Проблема:** Булевый тест содержит недопустимое значение
**Решение:** Используйте только: "+", "-", "+/-", "n.d."

#### Ошибка: "Missing value_type for numeric test"
**Проблема:** Для числового теста не указан value_type
**Решение:** Добавьте: "minimum", "maximum", "optimal", или "single"

#### Ошибка: "Invalid date format"
**Проблема:** Дата не в формате YYYY-MM-DD
**Решение:** Преобразуйте все даты к формату YYYY-MM-DD

#### Ошибка: "Strain not found"
**Проблема:** strain_identifier в TestResults не найден в Strains
**Решение:** Убедитесь, что все штаммы из TestResults есть в листе Strains

### 6. ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ

#### Создание backup перед импортом:
```bash
make backup-create
```

#### Восстановление из backup:
```bash
make restore-db BACKUP_FILE=имя_файла.sql.gz
```

#### Экспорт данных после импорта:
```bash
make export-data
```

### 7. ПРИМЕР ПОЛНОГО WORKFLOW

```bash
# 1. Запуск системы
make start

# 2. Создание backup
make backup-create

# 3. Импорт новых данных
make import-excel-all EXCEL_FILE=lysobacter_data.xlsx

# 4. Проверка результатов
make stats
make validate-data

# 5. Поиск конкретного штамма
make search-strain STRAIN_ID=LYS-001

# 6. При необходимости - восстановление
# make restore-db BACKUP_FILE=имя_файла.sql.gz
```

### 8. КОНТАКТЫ ПОДДЕРЖКИ

При возникновении проблем:
1. Проверьте логи: `make logs`
2. Проверьте статус: `make status`
3. Протестируйте подключение: `make test-connection`
4. Обратитесь с описанием ошибки и приложите файл Excel

### 9. ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После успешного импорта:
- ✅ Все штаммы добавлены в базу данных
- ✅ Все результаты тестов связаны со штаммами
- ✅ Статистика показывает корректные числа
- ✅ Поиск работает для всех штаммов
- ✅ Валидация проходит без ошибок

**СИСТЕМА ГОТОВА К ПРОДУКТИВНОМУ ИСПОЛЬЗОВАНИЮ!** 