#!/usr/bin/env python
"""
Скрипт для миграции данных из SQLite в PostgreSQL.

Использование:
    python scripts/migrate_sqlite_to_postgres.py

Перед запуском убедитесь, что:
    1. PostgreSQL база данных настроена и запущена
    2. Миграции Django применены к PostgreSQL
    3. Переменные окружения настроены правильно
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lr4'))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lr4.settings')
django.setup()

from django.db import connections
from flimsJSON.models import Film

def migrate_data():
    """Переносит данные из SQLite в PostgreSQL"""
    
    # Проверяем, что есть данные в SQLite
    sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lr4', 'db.sqlite3')
    
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite база данных не найдена: {sqlite_db_path}")
        return
    
    print("Начинаем миграцию данных из SQLite в PostgreSQL...")
    
    # Подключаемся к SQLite
    import sqlite3
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Проверяем существование таблицы в SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='flimsJSON_film'")
        if not sqlite_cursor.fetchone():
            print("Таблица flimsJSON_film не найдена в SQLite базе данных.")
            return
        
        # Получаем данные из SQLite
        sqlite_cursor.execute("SELECT title, genre, director, country, created_at FROM flimsJSON_film")
        films_data = sqlite_cursor.fetchall()
        
        if not films_data:
            print("Нет данных для миграции.")
            return
        
        print(f"Найдено {len(films_data)} записей для миграции.")
        
        # Переносим данные в PostgreSQL
        migrated_count = 0
        skipped_count = 0
        
        for title, genre, director, country, created_at in films_data:
            try:
                # Проверяем на дубликаты (используя unique_together из модели)
                if Film.objects.filter(title=title, director=director, country=country).exists():
                    print(f"Пропущено (дубликат): {title}")
                    skipped_count += 1
                    continue
                
                # Создаем запись в PostgreSQL
                Film.objects.create(
                    title=title,
                    genre=genre,
                    director=director,
                    country=country,
                    created_at=created_at if created_at else None
                )
                migrated_count += 1
                print(f"Перенесено: {title}")
                
            except Exception as e:
                print(f"Ошибка при переносе {title}: {str(e)}")
        
        print(f"\nМиграция завершена!")
        print(f"Перенесено записей: {migrated_count}")
        print(f"Пропущено (дубликаты): {skipped_count}")
        
    except Exception as e:
        print(f"Ошибка при миграции: {str(e)}")
    finally:
        sqlite_conn.close()

if __name__ == '__main__':
    migrate_data()

