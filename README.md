# Django Films Management Application

Django-приложение для управления фильмами с поддержкой сохранения данных в файлы JSON/XML или в базу данных PostgreSQL.

## Возможности

- ✅ Добавление фильмов с выбором хранилища (файл JSON или база данных PostgreSQL)
- ✅ Проверка на дубликаты при сохранении в БД
- ✅ Просмотр данных из файлов или базы данных
- ✅ AJAX-поиск по записям в базе данных
- ✅ Редактирование и удаление записей из БД
- ✅ Загрузка файлов JSON с валидацией
- ✅ Docker и Docker Compose для развертывания
- ✅ PostgreSQL для production

## Технологии

- Django 5.2.6
- PostgreSQL 15
- Docker & Docker Compose
- Bootstrap 5
- Python 3.11

## Требования

- Docker и Docker Compose (для развертывания через Docker)
- Python 3.11+ (для локальной разработки)

## Быстрый старт с Docker

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd lr4_Django
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл и установите необходимые значения:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

POSTGRES_DB=lr4_db
POSTGRES_USER=lr4_user
POSTGRES_PASSWORD=lr4_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Запуск приложения (Development)

```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

Приложение будет доступно по адресу: http://localhost:8000

### 4. Применение миграций

После первого запуска примените миграции базы данных:

```bash
docker-compose exec web python lr4/manage.py makemigrations
docker-compose exec web python lr4/manage.py migrate
```

### 5. Создание суперпользователя (опционально)

Для доступа к админ-панели Django:

```bash
docker-compose exec web python lr4/manage.py createsuperuser
```

Админ-панель доступна по адресу: http://localhost:8000/admin

## Production развертывание

Для production используйте `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

**Важно для production:**
- Установите `DEBUG=False` в `.env`
- Измените `SECRET_KEY` на безопасный
- Настройте `ALLOWED_HOSTS` правильно
- Используйте сильные пароли для PostgreSQL

## Миграция данных из SQLite в PostgreSQL

Если у вас есть данные в SQLite базе данных, которые нужно перенести в PostgreSQL:

### Метод 1: Использование скрипта миграции

1. Убедитесь, что PostgreSQL контейнер запущен и миграции применены
2. Запустите скрипт миграции:

```bash
docker-compose exec web python scripts/migrate_sqlite_to_postgres.py
```

### Метод 2: Ручная миграция через Django

```bash
# Экспорт данных из SQLite
docker-compose exec web python lr4/manage.py dumpdata flimsJSON > films_backup.json

# Импорт в PostgreSQL (убедитесь, что БД переключена на PostgreSQL)
docker-compose exec web python lr4/manage.py loaddata films_backup.json
```

## Локальная разработка (без Docker)

### 1. Создание виртуального окружения

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных

#### Использование SQLite (по умолчанию)

Ничего дополнительного делать не нужно, просто:

```bash
python lr4/manage.py migrate
python lr4/manage.py runserver
```

#### Использование PostgreSQL

1. Установите PostgreSQL локально
2. Создайте базу данных:

```sql
CREATE DATABASE lr4_db;
CREATE USER lr4_user WITH PASSWORD 'lr4_password';
ALTER ROLE lr4_user SET client_encoding TO 'utf8';
ALTER ROLE lr4_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lr4_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lr4_db TO lr4_user;
```

3. Создайте `.env` файл с настройками PostgreSQL:

```env
POSTGRES_DB=lr4_db
POSTGRES_USER=lr4_user
POSTGRES_PASSWORD=lr4_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

4. Примените миграции:

```bash
python lr4/manage.py migrate
python lr4/manage.py runserver
```

## Структура проекта

```
lr4_Django/
├── lr4/                    # Django проект
│   ├── lr4/               # Настройки проекта
│   │   ├── settings.py    # Настройки Django
│   │   ├── urls.py        # URL конфигурация
│   │   └── wsgi.py        # WSGI конфигурация
│   ├── manage.py          # Django management script
│   └── db.sqlite3         # SQLite БД (для локальной разработки)
├── flimsJSON/             # Django приложение
│   ├── models.py          # Модели данных
│   ├── views.py           # Представления
│   ├── forms.py           # Формы
│   ├── templates/         # HTML шаблоны
│   └── migrations/        # Миграции базы данных
├── scripts/               # Вспомогательные скрипты
│   └── migrate_sqlite_to_postgres.py  # Скрипт миграции данных
├── Dockerfile             # Docker образ для Django
├── docker-compose.yml     # Docker Compose для development
├── docker-compose.prod.yml # Docker Compose для production
├── requirements.txt       # Python зависимости
├── .env.example           # Пример файла с переменными окружения
├── .dockerignore          # Игнорируемые файлы для Docker
└── README.md              # Документация
```

## Основные команды Docker

```bash
# Запуск контейнеров
docker-compose up

# Запуск в фоновом режиме
docker-compose up -d

# Остановка контейнеров
docker-compose down

# Просмотр логов
docker-compose logs -f web
docker-compose logs -f db

# Выполнение команд в контейнере
docker-compose exec web python lr4/manage.py migrate
docker-compose exec web python lr4/manage.py createsuperuser

# Пересборка образов
docker-compose build --no-cache

# Очистка volumes (удалит данные БД!)
docker-compose down -v
```

## API и URL структура

- `/` - Главная страница
- `/film_add/` - Добавление фильма
- `/film_list/` - Список фильмов (с выбором источника данных)
- `/film_list/?source=file` - Просмотр из файлов
- `/film_list/?source=db` - Просмотр из базы данных
- `/film_edit/<id>/` - Редактирование фильма
- `/film_delete/<id>/` - Удаление фильма
- `/film_search/` - AJAX поиск (GET параметр `q`)
- `/admin/` - Админ-панель Django

## Функционал

### Выбор хранилища данных

При добавлении фильма можно выбрать:
- **Файл (JSON)** - данные сохраняются в `Films/films.json`
- **База данных** - данные сохраняются в PostgreSQL с проверкой на дубликаты

### Проверка на дубликаты

При сохранении в БД проверяется уникальность комбинации:
- Название фильма (title)
- Режиссёр (director)
- Страна производства (country)

Если такая запись уже существует, выводится соответствующее сообщение.

### AJAX поиск

Для записей в базе данных реализован AJAX-поиск по полям:
- Название фильма
- Жанр
- Режиссёр
- Страна производства

Поиск выполняется в реальном времени при вводе текста.

### CRUD операции

Для записей в базе данных доступны:
- **Create** - создание через форму
- **Read** - просмотр списка и детальной информации
- **Update** - редактирование с валидацией и проверкой на дубликаты
- **Delete** - удаление с подтверждением

## Разрешение проблем

### Ошибка подключения к базе данных

Убедитесь, что:
1. PostgreSQL контейнер запущен: `docker-compose ps`
2. Переменные окружения настроены правильно
3. Миграции применены: `docker-compose exec web python lr4/manage.py migrate`

### Статические файлы не загружаются

Выполните сбор статических файлов:

```bash
docker-compose exec web python lr4/manage.py collectstatic --noinput
```

### Ошибка при миграции данных

Проверьте:
1. SQLite файл существует и содержит данные
2. PostgreSQL база данных создана и миграции применены
3. Переменные окружения настроены правильно

## Безопасность

- **Никогда не коммитьте `.env` файл** в репозиторий
- Используйте сильные пароли для production
- Установите `DEBUG=False` для production
- Регулярно обновляйте зависимости

## Лицензия

Этот проект создан в образовательных целях.

## Автор

Разработано для лабораторной работы по Django.
