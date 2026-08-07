<div align="center">

# 🛡️ FSF Tools — Руководство пользователя (RU)

**File Sanitization Framework v2.1.0** — швейцарский нож для работы с метаданными файлов.

[English README](README.md) • [Репозиторий GitHub](https://github.com/Svargentyur/fsf-tools)

<br />

![FSF Tools Screenshot](docs/screenshot.png)

</div>

---

## 📖 Оглавление

1. [Особенности и отличие от аналогов](#features)
2. [Быстрая установка](#install)
3. [Поддерживаемые форматы](#formats)
4. [Подробный разбор команд (16 шт.)](#commands)
   - [Просмотр метаданных (`fsf view`)](#cmd-view)
   - [Очистка метаданных (`fsf clean`)](#cmd-clean)
   - [Хирургическое удаление (`fsf strip`)](#cmd-strip) `NEW`
   - [Ручная подмена (`fsf spoof`)](#cmd-spoof)
   - [Реалистичная подмена (`fsf randomize`)](#cmd-randomize)
   - [Создание фейковой личности (`fsf forge`)](#cmd-forge)
   - [Таймлайн поездки (`fsf timeline`)](#cmd-timeline) `NEW`
   - [Хеши файлов (`fsf hash`)](#cmd-hash) `NEW`
   - [Шаблоны метаданных (`fsf template`)](#cmd-template) `NEW`
   - [Криминалистическая проверка (`fsf audit`)](#cmd-audit)
   - [Сравнение файлов (`fsf compare`)](#cmd-compare)
   - [Пакетная обработка (`fsf batch`)](#cmd-batch)
   - [Анализ рисков приватности (`fsf report`)](#cmd-report)
   - [Просмотр пресетов (`fsf presets`)](#cmd-presets)
   - [Экспорт в JSON (`fsf export`)](#cmd-export)
   - [Копирование метаданных (`fsf clone`)](#cmd-clone)
5. [Пресеты камер, городов и сцен](#presets)
6. [Разработка и тесты](#dev)

---

<a id="features"></a>
## ✨ Особенности и отличие от аналогов

| Возможность | FSF Tools 🛡️ | ExifTool 📸 | MAT2 🧹 |
| :--- | :---: | :---: | :---: |
| **Основная философия** | **Генерация правдоподобных фейков** | Чтение/запись тегов вручную | Полное удаление всего |
| **Требования к знаниям** | **Автоматизировано (пресеты/профили)** | Нужны глубокие знания тегов | Не нужны (просто стирает) |
| **Физическая корреляция** | **Да (связь ISO, выдержки и диафрагмы)** | Нет | Н/А |
| **Подделка личности (`forge`)** | **Да (серии фото от одного человека)** | Нет | Нет |
| **Forensic Audit** | **Встроенный детектор аномалий** | Нет | Нет |
| **Хирургическое удаление** | **Да (GPS / даты / камера / миниатюра)** | Ручное по тегам | Всё или ничего |
| **Таймлайн поездки** | **Да (GPS дрифт по hotspots)** | Нет | Нет |
| **Мутация хешей** | **Да (изменение хеша без порчи файла)** | Нет | Нет |
| **Шаблоны метаданных** | **Да (сохранение/загрузка YAML)** | Частично (argfiles) | Нет |

---

<a id="install"></a>
## 🚀 Быстрая установка

### Способ 1: Из PyPI через pip

```bash
pip install fsf-tools
```

### Способ 2: Клонирование и локальная установка

```bash
git clone https://github.com/Svargentyur/fsf-tools.git
cd fsf-tools
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Проверка установки:
```bash
fsf --version
```

---

<a id="formats"></a>
## 📁 Поддерживаемые форматы

| Формат | View | Clean | Spoof | Strip | Clone |
|--------|:---:|:---:|:---:|:---:|:---:|
| **JPEG / PNG / TIFF / WebP** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **MP3 / FLAC / OGG / M4A** | ✅ | ✅ | ✅ | — | ✅ |
| **PDF** | ✅ | ✅ | ✅ | — | ✅ |
| **DOCX / XLSX / PPTX** | ✅ | ✅ | ✅ | — | ✅ |

---

<a id="commands"></a>
## 📋 Подробный разбор команд (16 шт.)

<a id="cmd-view"></a>
### 1. `fsf view` — Просмотр метаданных
Отображает все найденные EXIF, ID3, PDF и DocumentInfo метаданные в виде красивой таблицы.

```bash
fsf view photo.jpg
fsf view --json document.pdf
```

<a id="cmd-clean"></a>
### 2. `fsf clean` — Полная очистка
Удаляет ВСЕ метаданные из файла (EXIF, GPS, имя автора, программное обеспечение).

```bash
fsf clean photo.jpg
fsf clean photo.jpg -o clean_photo.jpg
```

<a id="cmd-strip"></a>
### 3. `fsf strip` — Хирургическое удаление `NEW v2.1.0`
Удаляет **только указанные категории** метаданных, оставляя всё остальное нетронутым.

```bash
fsf strip photo.jpg --gps              # Только GPS/геолокация
fsf strip photo.jpg --dates            # Только даты и время
fsf strip photo.jpg --device           # Только камера (make/model/serial)
fsf strip photo.jpg --thumbnail        # Встроенная миниатюра (риск приватности!)
fsf strip photo.jpg --all              # Все категории сразу
fsf strip photo.jpg --gps --dates -o safe.jpg   # Комбинация с сохранением копии
```

<a id="cmd-spoof"></a>
### 4. `fsf spoof` — Ручная подмена
Позволяет вручную задать конкретную камеру, город, автора или дату.

```bash
fsf spoof photo.jpg --preset iphone_15_pro --city tokyo --sync-time
fsf spoof doc.docx --author "Иван Иванов" --title "Открытый отчет"
```

<a id="cmd-randomize"></a>
### 5. `fsf randomize` — Реалистичная подмена
Генерирует физически корректные метаданные с учетом треугольника экспозиции (ISO ↔ Выдержка ↔ Диафрагма).

```bash
fsf randomize photo.jpg
fsf randomize photo.jpg --scene night_street --city tokyo --preset sony_a7iv --sync-time
```

<a id="cmd-forge"></a>
### 6. `fsf forge` — Создание фейковой личности
Генерирует консистентную персону и применяет её к серии файлов.

```bash
fsf forge *.jpg --locale jp --city kyoto --camera fuji_xt5 -o ./output/
```

Доступные локали имен: `en`, `de`, `jp`, `es`, `ru`, `kr`.

<a id="cmd-timeline"></a>
### 7. `fsf timeline` — Таймлайн поездки `NEW v2.1.0`
Генерирует реалистичную последовательность фото как будто сделанных во время поездки: хронологический порядок, GPS drift между достопримечательностями, автоматическая смена сцен по времени суток.

```bash
# 3-дневная поездка в Токио на Sony:
fsf timeline *.jpg --city tokyo --preset sony_a7iv --days 3 --sync-time

# 5-дневная поездка в Париж в стиле энтузиаста:
fsf timeline *.jpg --city paris --style enthusiast --days 5

# Профессиональная съемка в Берлине:
fsf timeline *.jpg --city berlin --style professional --days 1 -o ./output/
```

Стили съемки (`--style`):
- `casual` — турист с телефоном (5-15 фото/день)
- `enthusiast` — хоббист с беззеркалкой (15-40 фото/день)
- `professional` — рабочий фотограф (50-200 фото/день)

<a id="cmd-hash"></a>
### 8. `fsf hash` — Хеши файлов `NEW v2.1.0`
Вычисление, верификация и мутация хешей.

```bash
# Вычислить MD5, SHA1, SHA256:
fsf hash photo.jpg

# Конкретный алгоритм:
fsf hash photo.jpg -a sha512

# Мутация хеша (добавляет байты, меняющие хеш без порчи файла):
fsf hash photo.jpg --mutate
fsf hash photo.jpg --mutate -o mutated.jpg

# Проверка хеша:
fsf hash photo.jpg --verify abc123def456...
```

<a id="cmd-template"></a>
### 9. `fsf template` — Шаблоны метаданных `NEW v2.1.0`
Сохранение, загрузка и применение YAML-профилей метаданных.

```bash
# Извлечь метаданные из файла и сохранить как шаблон:
fsf template save photo.jpg my_preset -d "Токийский ночной пресет"

# Посмотреть список шаблонов:
fsf template list

# Просмотреть содержимое шаблона:
fsf template load my_preset

# Применить шаблон к другому файлу:
fsf template apply my_preset target.jpg

# Удалить шаблон:
fsf template delete my_preset
```

Шаблоны хранятся в `~/.config/fsf-tools/templates/` в формате YAML.

<a id="cmd-audit"></a>
### 10. `fsf audit` — Криминалистическая проверка
Проверяет файл на аномалии (10 проверок).

```bash
fsf audit photo.jpg
```

<a id="cmd-compare"></a>
### 11. `fsf compare` — Сравнение двух файлов

```bash
fsf compare original.jpg spoofed.jpg
```

<a id="cmd-batch"></a>
### 12. `fsf batch` — Пакетная обработка

```bash
fsf batch ./photos/ --action clean -r
fsf batch ./photos/ --action randomize --preset iphone_15_pro -o ./clean_photos/
```

<a id="cmd-report"></a>
### 13. `fsf report` — Анализ рисков приватности

```bash
fsf report photo.jpg
```

<a id="cmd-presets"></a>
### 14. `fsf presets` — Список пресетов

```bash
fsf presets --cameras
fsf presets --cities
```

<a id="cmd-export"></a>
### 15. `fsf export` — Экспорт метаданных

```bash
fsf export photo.jpg -o metadata.json
```

<a id="cmd-clone"></a>
### 16. `fsf clone` — Копирование метаданных

```bash
fsf clone source.jpg target.jpg -o output.jpg
```

---

<a id="presets"></a>
## 🎨 Пресеты камер, городов и сцен

### Камеры (18 пресетов):
- **Apple**: iPhone 15 Pro, iPhone 14
- **Samsung**: Galaxy S24 Ultra, Galaxy S23
- **Google**: Pixel 8 Pro, Pixel 7
- **Sony**: Alpha 7 IV, Alpha 7R V
- **Canon**: EOS R5, EOS R6 Mark II
- **Nikon**: Z8, Z6 III
- **Fujifilm**: X-T5, X-H2
- **Leica**: Q3
- **Ricoh**: GR III
- **GoPro**: HERO12 Black
- **DJI**: Mavic 3 Pro

### Сцены (`--scene`):
- `daylight_outdoor` — яркий дневной свет (ISO 100, высокая выдержка)
- `golden_hour` — закатный/рассветный свет
- `indoor` — помещение (среднее ISO, выдержка 1/60s)
- `night_street` — ночной город (ISO 3200-6400, открытая диафрагма)
- `portrait` — портрет (боке, f/1.4-f/2.8)
- `landscape` — пейзаж (f/8-f/11, ISO 100)

---

<a id="dev"></a>
## 🧪 Разработка и тесты

```bash
git clone https://github.com/Svargentyur/fsf-tools.git
cd fsf-tools
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v  # 27 тестов
```

---

## 📝 Лицензия

Проект распространяется под защищенной Copyleft-лицензией [GNU General Public License v3.0 (GPLv3)](LICENSE). Проект свободен для использования, но запрещает закрывать исходный код и перепродавать софт без публикации исходников.
