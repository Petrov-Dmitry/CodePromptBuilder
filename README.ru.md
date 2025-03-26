# Code Prompt Builder
Инструмент для создания promt для чат-ботов из кода проекта

[English documentation](README.md)

## Возможности
- Рекурсивное сканирование проектов
- Поддержка `.gitignore`
- Дополнительные исключения через --exclude
- Работа с бинарными файлами и Unicode-именами
- Кроссплатформенность (Windows/macOS/Linux)

## Требования
- Python 3.6+
- Дополнительные зависимости не требуются

## Установка
Просто загрузите `code_prompt_builder.py` в каталог проектов.

## Использование
```bash
python code_prompt_builder.py PROJECT_DIR [OUTPUT_FILE] [--exclude PATTERN1 PATTERN2...]
```

### Справочное сообщение
Используйте параметр `-h` для просмотра справочного сообщения

### Примеры платформ

#### Windows
- Базовое использование
```
python code_prompt_builder.py C:\my_project project_code.txt
```
- Исключить временные файлы
```
python code_prompt_builder.py C:\my_project output.txt --exclude "*.tmp" "build\*"
```

#### macOS/Linux
- Базовое использование
```
python3 code_prompt_builder.py ./my_project output.txt
```

- Исключить скрытые и подкачанные файлы
```
python3 code_prompt_builder.py ./my_project output.txt --exclude ".*" "*.swp"
```

## Тестирование
Запустите тесты с помощью:
```
python -m unittest test_code_prompt_builder.py
```
