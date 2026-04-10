# Scripts for Notes

Инструмент для управления ссылками и backlinks в markdown-файлах.

## Возможности

- Конвертация вики-ссылок `[[name]]` → `[name](name.md)`
- Исправление путей к медиафайлам
- Автоматическое управление backlinks
- Поддержка Python и Lua версий

## Установка

### Python

```bash
pip install -r requirements.txt
```

### Lua

Требуется Lua 5.1+ и LuaFileSystem:
```bash
luarocks install luafilesystem
```

## Использование

### Python

```bash
# Конвертация вики-ссылок
python links.py -w

# Обновление backlinks
python links.py -b

# Исправление путей к медиа (с указанием корневой директории)
python links.py -p /path/to/media

# Рабочая директория
python links.py -d /path/to/notes

# Подробный вывод
python links.py -v

# Комбинирование опций
python links.py -w -b -v -d ./notes
```

### Lua

```bash
# Конвертация вики-ссылок
lua lua/init.lua -w

# Обновление backlinks
lua lua/init.lua -b

# Все опции аналогичны Python версии
lua lua/init.lua -w -b -v -d ./notes
```

## Опции CLI

| Опция | Описание |
|-------|----------|
| `-w`, `--wiki` | Конвертировать вики-ссылки `[[name]]` в markdown `[name](name.md)` |
| `-b`, `--back` | Обновить backlinks в файлах |
| `-p`, `--path` | Корневой путь для медиафайлов |
| `-d`, `--dir` | Рабочая директория |
| `-v`, `--verbose` | Подробный вывод |
| `-h`, `--help` | Показать справку |

## Структура backlinks

Файлы должны содержать секцию `backlinks:` в формате:

```markdown
# Заметка

Содержимое заметки...

backlinks:
- [Другая заметка](другая_заметка.md)
```

Скрипт автоматически:
1. Находит все ссылки `[link](file.md)` в заметках
2. Определяет, на какие файты ссылаются
3. Добавляет обратные ссылки в соответствующие файлы

## Архитектура

### Python

```
modules/
├── cli.py             - Обработка аргументов командной строки
├── link_processor.py - Конвертация вики-ссылок
├── backlinks.py       - Управление backlinks
└── file_utils.py      - Утилиты для работы с файлами
```

### Lua

```
lua/
├── cli.lua            - CLI
├── link_processor.lua
├── backlinks.lua
└── file_utils.lua
```

## Примеры

### Конвертация вики-ссылок

До:
```markdown
[[Моя заметка]]
```

После:
```markdown
[Моя заметка](Моя заметка.md)
```

### Работа с backlinks

Файл `note1.md`:
```markdown
# Note 1

Смотри также [[Note 2]]

backlinks:
```

Файл `note2.md`:
```markdown
# Note 2

backlinks:
- [Note 1](note1.md)
```

После запуска `python links.py -b` backlinks автоматически обновятся.

## Лицензия

MIT