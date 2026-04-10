# План рефакторинга + миграции на Lua

## Этап 1: Рефакторинг Python

### 1.1 Устранение дублирования

| Файл | Действие |
|------|----------|
| `modules/filesutils.py` | Удалить строки 12-18 (дубликат `find_files_with_extension`) |
| `modules/filesutils.py` | Добавить `__all__ = ['find_files_with_extension']` |

### 1.2 Исправление багов

| Файл:строка | Проблема | Исправление |
|-------------|----------|-------------|
| `links.py:41` | Неверный regex `\1` | `replace_in_file(file_path, r'!\[\[(.*)\]\]', r'![\1](\1)')` |
| `links.py:71` | `return` без значения при ошибке | Добавить `return False`, обработать в вызывающем коде |
| `links.py:117` | Пустой return | `return None` вместо пустого `return` |

### 1.3 Рефакторинг архитектуры

```
modules/
├── __init__.py
├── file_utils.py      (из filesutils.py, переименовать)
├── link_processor.py  (функции обработки ссылок из links.py)
├── backlinks.py       (функции backlinks)
└── cli.py             (обработка аргументов)
```

**Новые модули:**
- `modules/cli.py` — argparse, вызов функций
- `modules/link_processor.py` — `replace_wiki_links_in_file`, `replace_media_wiki_links_in_file`, `fix_media_path_in_file`
- `modules/backlinks.py` — `find_links`, `find_new_backlinks`, `add_new_backlinks`

### 1.4 Улучшения
- Добавить type hints
- Вынести константы `LINKS = 0`, `BACKLINKS = 1` в enum
- Добавить docstrings

---

## Этап 2: Lua-версия (CLI, Lua 5.1)

### 2.1 Структура проекта

```
lua/
├── init.lua           -- точка входа
├── file_utils.lua     -- поиск файлов
├── link_processor.lua -- конвертация ссылок
├── backlinks.lua      -- управление backlinks
└── cli.lua            -- argparse
```

### 2.2 Зависимости
- `luafilesystem` — для `lfs.dir`, `lfs.attributes`
- Стандартный `io`, `os`, `string`, `table`

### 2.3 Реализация функций

**file_utils.lua:**
```lua
local M = {}

function M.find_files(extension, root)
    local files = {}
    local iter = lfs.dir(root or '.')
    for file in iter do
        if file:ends_with(extension) then
            table.insert(files, file)
        end
    end
    return files
end
```

**link_processor.lua:**
```lua
-- wiki links [[name]] -> [name](name.md)
function M.wiki_to_markdown(content)
    return content:gsub('%[%[(.-)%]%]', ' [%1](%1.md)')
end
```

**cli.lua:**
- `-w, --wiki` — конвертация вики-ссылок
- `-b, --back` — backlinks
- `-d, --dir` — директория
- `-v` — verbose

---

## Этап 3: Новые возможности (оба языка)

| Фича | Python | Lua |
|------|--------|-----|
| `--dry-run` | + | + |
| `--output json` | + | + |
| Логирование в файл | + | + |

---

## Порядок выполнения

1. **Python** — исправить баги → рефакторинг в модули → добавить фичи
2. **Lua** — создать структуру → реализовать функции → CLI