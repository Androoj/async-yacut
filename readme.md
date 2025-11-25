# YaCut

## Описание проекта

YaCut — это сервис укорачивания ссылок, который позволяет превратить длинные и неудобные URL в короткие и легко читаемые. Например, из  
https://practicum.yandex.ru/trainer/backend-developer/lesson/12e07d96-31f3-449f-abcf-e468b6a39061/  
можно получить  
http://yacut.ru/12e07d.

Проект также включает дополнительную функцию: асинхронную загрузку нескольких файлов на Яндекс.Диск с автоматической генерацией коротких ссылок для скачивания каждого из них.

Сервис поддерживает как ручное, так и автоматическое создание коротких идентификаторов и работает через удобный веб-интерфейс, а также предоставляет публичное REST API.

## Функциональность

1. Укорачивание длинных ссылок:
- с автоматически сгенерированным идентификатором (6 символов: латинские буквы + цифры);
- с пользовательским коротким идентификатором (до 16 символов).
2.  Проверка уникальности коротких идентификаторов.
3.  Переадресация по короткой ссылке на оригинальный адрес.
4.  Асинхронная загрузка нескольких файлов на Яндекс.Диск через отдельную страницу /files.
5.  Автоматическая генерация коротких ссылок для скачивания загруженных файлов.
6.  Обработка конфликтов: невозможность использовать /files в качестве короткой ссылки или занять уже существующий идентификатор.

### Публичный API:
- POST /api/id/ — создание новой короткой ссылки;
- GET /api/id/<short_id>/ — получение оригинальной ссылки по короткому идентификатору.

<sub>Загрузка файлов возможна только через веб-интерфейс. API для файлов не предусмотрен.</sub> 

## Технологический стек
- ![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![Flask](https://img.shields.io/badge/Flask-2.3%2B-000000?style=for-the-badge&logo=flask&logoColor=white)
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-000000?style=for-the-badge&logo=sqlalchemy&logoColor=white)
- ![SQLite](https://img.shields.io/badge/SQLite-3-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
- ![aiohttp](https://img.shields.io/badge/aiohttp-3.8%2B-FF5733?style=for-the-badge&logo=python&logoColor=white)
- ![Jinja2](https://img.shields.io/badge/Jinja2-3.0%2B-000000?style=for-the-badge&logo=python&logoColor=white)
- ![WTForms](https://img.shields.io/badge/WTForms-3.0%2B-000000?style=for-the-badge&logo=python&logoColor=white)

## Как запустить проект Yacut:

### Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/Androoj/async-yacut.git
cd async-yacut
```

### Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

- **Если у вас Linux/macOS:**

```bash
source venv/bin/activate
```

- **Если у вас windows:**

```bash
source venv/scripts/activate
```

### Установить зависимости из файла requirements.txt:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Создать в корнейвой директории проекта файл .env:

```env
FLASK_APP=yacut
SECRET_KEY=ваш_секретный_ключ
DATABASE_URI=sqlite:///db.sqlite
DISK_TOKEN=ваш_токен_яндекс_диска
DEBUG=True
API_VERSION=версия_апи
```

> **DISK_TOKEN** — OAuth-токен приложения ЯндексДиска.

### Создать базу данных и применить миграции:

```bash
flask db upgrade
```

### Запустить проект:

```bash
flask run
```

## API

Сервис предоставляет публичный REST API для управления короткими ссылками.  
**Спецификация OpenAPI доступна по адресу: /api/docs (возвращает файл openapi.yml в формате YAML).**

### Эндпоинты:

| Метод | Эндпоинт               | Описание                              | Тело запроса (JSON)                                                                 | Ответ (успех)                                                                 |
|-------|------------------------|---------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| POST  | `/api/id/`             | Создание короткой ссылки              | ```{ "url": "https://example.com", "custom_id": "mylink" }```<br>`custom_id` — опционально | ```{ "url": "https://example.com", "short_link": "http://localhost/mylink" }``` |
| GET   | `/api/id/<short_id>/`  | Получение оригинальной ссылки по ID   | —                                                                                   | ```{ "url": "https://example.com" }```                                         |

### Возможные ошибки:

При некорректных запросах API возвращает статус 400 или 404 с телом:

```json
{ "message": "Описание ошибки" }
```

### Примеры сообщений об ошибках:

- "Отсутствует тело запроса"
- "url" является обязательным полем!
- "Указано недопустимое имя для короткой ссылки"
- "Предложенный вариант короткой ссылки уже существует."
- "Указанный id не найден"

<sub>Полная спецификация API описана в файле openapi.yml , который можно визуализировать в Swagger Editor . </sub>

#### Автор: [Юрков Андрей](https://github.com/Androoj)