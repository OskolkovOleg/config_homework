# Конфигурационный транслятор Вариант 17

Инструмент командной строки для преобразования учебного конфигурационного языка в XML.

## Описание

Проект реализует транслятор для конфигурационного языка с поддержкой:

- Однострочных комментариев `-- комментарий`
- Многострочных комментариев `%{ комментарий %}`
- Чисел: `[+-]?([1-9][0-9]*|0)`
- Словарей: `([ имя: значение, имя: значение ])`
- Имен: `[a-zA-Z][_a-zA-Z0-9]*`
- Объявления констант: `имя: значение;`
- Вычисления констант: `${имя}`

Используется Lark для синтаксического разбора.

## Установка

```bash
pip install lark-parser pytest
```

## Использование

```bash
python config_parser.py -i <входной_файл> -o <выходной_файл>
```

Пример:

```bash
python config_parser.py -i examples/webserver.conf -o output.xml
```

## Структура проекта

```
config_homework/
├── config_parser.py      # Основной скрипт
├── grammar.lark          # Грамматика языка
├── test_parser.py        # Тесты
├── examples/             # Примеры конфигураций
│   ├── webserver.conf    # Веб-сервер
│   ├── database.conf     # База данных
│   └── game.conf         # Игровые настройки
└── README.md
```

## Тестирование

```bash
pytest test_parser.py -v
```

Тесты покрывают все конструкции языка, включая вложенные словари.

## Примеры

### Пример 1: Веб-сервер

**Входной файл** ([examples/webserver.conf](examples/webserver.conf)):

```
-- Конфигурация веб-сервера

port: 8080;
timeout: 30;

server_config: ([
  host: 80,
  max_connections: 100,
  ssl_enabled: 1
]);

active_port: ${port};
```

### Пример 2: База данных

**Входной файл** ([examples/database.conf](examples/database.conf)):

```
%{
Конфигурация базы данных
%}

db_port: 5432;
max_pool: 50;

connection: ([
  host: 127,
  port: ${db_port},
  pool_size: ${max_pool},
  settings: ([
    timeout: 60,
    retry: 3
  ])
]);
```

### Пример 3: Игра

**Входной файл** ([examples/game.conf](examples/game.conf)):

```
player_count: 4;
level: 10;

game_settings: ([
  max_players: ${player_count},
  difficulty: ${level},
  mode: 2,
  features: ([
    pvp: 1,
    pve: 1
  ])
]);
```

## Выходной формат XML

```xml
<?xml version="1.0" ?>
<config>
  <constant name="port">8080</constant>
  <constant name="timeout">30</constant>
  <constant name="server_config">
    <dictionary>
      <pair key="host">80</pair>
      <pair key="max_connections">100</pair>
      <pair key="ssl_enabled">1</pair>
    </dictionary>
  </constant>
  <constant name="active_port">8080</constant>
</config>
```

## Требования

- Python 3.7+
- lark>=1.1.0
- pytest>=7.0.0 (для тестов)

Установка зависимостей:

```bash
pip install -r requirements.txt
```
