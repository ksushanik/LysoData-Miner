#!/usr/bin/env python3
"""
Создание шаблона Excel файла для импорта данных штаммов лизобактерий.
Демонстрирует правильный формат данных.
"""

import pandas as pd
from datetime import datetime
import os

def create_excel_template():
    """Создает шаблон Excel файла с примерами данных."""
    
    # ЛИСТ 1: Strains (Информация о штаммах)
    strains_data = {
        'strain_identifier': [
            'LYS-001',
            'LYS-002', 
            'ATCC-123',
            'DSM-456'
        ],
        'scientific_name': [
            'Lysobacter enzymogenes',
            'Lysobacter antibioticus',
            'Lysobacter gummosus',
            'Lysobacter brunescens'
        ],
        'common_name': [
            'Strain C3',
            'Biocontrol strain B',
            'Gummy strain',
            'Brown pigment strain'
        ],
        'description': [
            'Highly active biocontrol strain isolated from rhizosphere',
            'Antibiotic-producing strain with broad spectrum activity',
            'Produces extracellular polysaccharides',
            'Dark pigmented strain with unique metabolic properties'
        ],
        'isolation_source': [
            'Rhizosphere soil',
            'Agricultural soil',
            'Marine sediment',
            'Forest soil'
        ],
        'isolation_location': [
            'Agricultural field, Germany',
            'Crop field, Netherlands',
            'Coastal area, Japan',
            'Deciduous forest, Canada'
        ],
        'isolation_date': [
            '2023-05-15',
            '2023-06-20',
            '2022-08-10',
            '2023-01-05'
        ],
        'notes': [
            'Shows strong antifungal activity against plant pathogens',
            'Produces multiple bioactive compounds',
            'Thermostable enzyme producer',
            'Novel strain with unique characteristics'
        ]
    }
    
    # ЛИСТ 2: TestResults (Результаты тестов)
    test_results_data = {
        'strain_identifier': [
            # Морфологические тесты для LYS-001 (only motility)
            'LYS-001',
            # Физиологические тесты для LYS-001  
            'LYS-001', 'LYS-001', 'LYS-001', 'LYS-001', 'LYS-001', 'LYS-001',
            # Биохимические тесты для LYS-001
            'LYS-001', 'LYS-001', 'LYS-001', 'LYS-001',
            # Утилизация сахаров для LYS-001
            'LYS-001', 'LYS-001', 'LYS-001',
            # Примеры для других штаммов (3 entries now)
            'LYS-002', 'ATCC-123', 'DSM-456'
        ],
        'test_code': [
            # Морфологические тесты (spore_formation removed - all Lysobacter are non-spore-forming)
            'motility',
            # Физиологические тесты (диапазоны температуры и pH)
            'temperature', 'temperature', 'temperature',
            'ph_level', 'ph_level', 'salt_tolerance',
            # Биохимические тесты
            'catalase', 'oxidase', 'proteolytic_activity', 'starch',
            # Утилизация сахаров
            'glucose_fermentation', 'maltose', 'lactose',
            # Другие штаммы (spore_formation removed)
            'catalase', 'motility', 'temperature'
        ],
        'result_value': [
            # LYS-001 морфологические (only motility)
            '+',
            # LYS-001 физиологические (температурный диапазон)
            '15', '35', '25',  # мин, макс, оптимальная температура
            '6.0', '8.5', '+', # pH диапазон и солеустойчивость
            # LYS-001 биохимические
            '+', '+', '+', '+',
            # LYS-001 утилизация сахаров
            '+', '+', '-',
            # Другие штаммы (3 entries)
            '+', '+/-', '20'
        ],
        'value_type': [
            # Булевые тесты (only motility)
            '',
            # Числовые тесты (обязательно указать тип)
            'minimum', 'maximum', 'optimal',
            'minimum', 'maximum', '',
            # Булевые тесты
            '', '', '', '',
            # Булевые тесты
            '', '', '',
            # Другие штаммы (3 entries)
            '', '', 'optimal'
        ],
        'measurement_unit': [
            # Морфологические (only motility)
            '',
            # Температура
            '°C', '°C', '°C',
            # pH
            'pH', 'pH', '',
            # Биохимические (без единиц)
            '', '', '', '',
            # Утилизация (без единиц)
            '', '', '',
            # Другие штаммы (3 entries)
            '', '', '°C'
        ],
        'confidence_level': [
            'high',
            'high', 'high', 'high',
            'high', 'medium', 'high',
            'high', 'high', 'high', 'high',
            'high', 'high', 'medium',
            'high', 'low', 'high'
        ],
        'tested_date': [
            '2023-06-01',
            '2023-06-02', '2023-06-02', '2023-06-02',
            '2023-06-02', '2023-06-02', '2023-06-03',
            '2023-06-03', '2023-06-03', '2023-06-04', '2023-06-04',
            '2023-06-05', '2023-06-05', '2023-06-05',
            '2023-06-10', '2023-06-12', '2023-06-13'
        ],
        'notes': [
            'Strong motility under microscope',
            'Minimum growth temperature',
            'Maximum growth temperature', 
            'Optimal growth temperature',
            'Minimum pH for growth',
            'pH tolerance test - moderate result',
            'Tolerates 3% NaCl',
            'Strong positive reaction',
            'Positive oxidase test',
            'Strong proteolytic activity',
            'Starch hydrolysis positive',
            'Glucose fermentation observed',
            'Maltose utilization confirmed',
            'No lactose utilization',
            'Catalase test positive',
            'Weak motility observed',
            'Optimal growth temperature'
        ]
    }
    
    # Создание DataFrame
    strains_df = pd.DataFrame(strains_data)
    test_results_df = pd.DataFrame(test_results_data)
    
    # Сохранение в Excel файл с двумя листами
    output_file = 'LYSOBACTER_DATA_TEMPLATE.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        strains_df.to_excel(writer, sheet_name='Strains', index=False)
        test_results_df.to_excel(writer, sheet_name='TestResults', index=False)
    
    print(f"✓ Шаблон Excel создан: {output_file}")
    print(f"✓ Штаммов в шаблоне: {len(strains_df)}")
    print(f"✓ Результатов тестов в шаблоне: {len(test_results_df)}")
    
    # Создание сводки
    summary = f"""
СВОДКА ШАБЛОНА EXCEL ФАЙЛА
=========================

ЛИСТ "Strains":
- Количество штаммов: {len(strains_df)}
- Колонки: {', '.join(strains_df.columns)}

ЛИСТ "TestResults":  
- Количество записей: {len(test_results_df)}
- Колонки: {', '.join(test_results_df.columns)}
- Тестируемые коды: {', '.join(sorted(test_results_df['test_code'].unique()))}

ТИПЫ ТЕСТОВ В ШАБЛОНЕ:
- Морфологические: motility (spore_formation removed - all Lysobacter are non-spore-forming)
- Физиологические: temperature, ph_level, salt_tolerance  
- Биохимические: catalase, oxidase, proteolytic_activity, starch
- Утилизация: glucose_fermentation, maltose, lactose

ПРИМЕРЫ ФОРМАТОВ:
- Булевы тесты: '+', '-', '+/-', 'n.d.'
- Числовые тесты: числа с указанием value_type (minimum/maximum/optimal)
- Даты: YYYY-MM-DD формат
- Уровни уверенности: high, medium, low

ГОТОВ ДЛЯ ИМПОРТА В БАЗУ ДАННЫХ!
"""
    
    # Сохранение сводки
    with open('TEMPLATE_SUMMARY.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(summary)
    
    return output_file

if __name__ == "__main__":
    create_excel_template() 