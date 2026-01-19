# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . /app/

# Копируем и делаем исполняемым entrypoint скрипт
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Создаем директории для статических файлов и медиа
RUN mkdir -p /app/staticfiles /app/media

# Открываем порт
EXPOSE 8000

# Используем entrypoint для инициализации
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда запуска (переопределяется в docker-compose)
CMD ["python", "lr4/manage.py", "runserver", "0.0.0.0:8000"]

