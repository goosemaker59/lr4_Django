from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .forms import FilmsForm, FileForm, FilmEditForm
from .models import Film
from django.conf import settings
from datetime import datetime
import os
import json
import uuid

FILM_REQUIRED_KEYS = ["title", "genre", "director", "country"]

# Проверка на корректность структуры
def validate_film_structure(js):
    def check_entry(entry):
        # Поддержка старого формата с "gerne" и нового с "genre"
        keys_to_check = ["title", "director", "country"]
        if "genre" in entry or "gerne" in entry:
            keys_to_check.append("genre" if "genre" in entry else "gerne")
        return all(k in entry for k in keys_to_check)
    if isinstance(js, list):
        return all(check_entry(item) for item in js)
    if isinstance(js, dict):
        return check_entry(js)
    return False

def index(request):
    response = render(request, "index.html", {})
    return response

def film_list(request):
    source = request.GET.get('source', 'file')  # 'file' or 'db'
    error_message = None
    success_message = None
    
    if request.method == 'POST':
        file_form = FileForm(request.POST, request.FILES)
        error_message = None
        if file_form.is_valid():
            title = file_form.cleaned_data['title']
            uploaded_file = file_form.cleaned_data['file']

            ext = os.path.splitext(uploaded_file.name)[1]
            unique_name = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(settings.MEDIA_ROOT, unique_name)
            # Сохраняем файл
            with open(file_path, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
            # ВАЛИДАЦИЯ JSON + СТРУКТУРЫ
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    jsdata = json.load(f)
                if not validate_film_structure(jsdata):
                    raise ValueError('invalid structure')
            except Exception:
                os.remove(file_path)
                error_message = 'Файл повреждён, не является корректным JSON или структура не совпадает.'
            else:
                # Сохраняем метаданные в JSON
                save_file_metadata(
                    filename=unique_name,
                    original_name=uploaded_file.name,
                    title=title,
                    size=uploaded_file.size
                )
                return redirect('film_list')
        else:
            error_message = 'Ошибка загрузки файла.'
    else:
        file_form = FileForm()
        error_message = None

    # Получаем данные в зависимости от источника
    if source == 'db':
        try:
            films = list(Film.objects.all())  # Преобразуем QuerySet в список
        except Exception as e:
            films = []
            error_message = f'Ошибка при получении данных из БД: {str(e)}. Убедитесь, что миграции применены.'
    else:
        films_data = get_file_data()
        films = films_data

    response = render(request, "film_list.html", {
        "file_form": file_form,
        "films": films,
        "error_message": error_message,
        "success_message": success_message,
        "source": source,
    })
    return response

def film_add(request):
    if request.method == 'POST':
        films_form = FilmsForm(request.POST)
        if films_form.is_valid():
            storage_type = films_form.cleaned_data['storage_type']
            film_data = {
                'title': films_form.cleaned_data['title'],
                'genre': films_form.cleaned_data['genre'],
                'director': films_form.cleaned_data['director'],
                'country': films_form.cleaned_data['country'],
            }
            
            if storage_type == 'database':
                # Сохранение в БД с проверкой на дубликаты
                duplicate_message = save_film_to_database(film_data)
                if duplicate_message:
                    messages.warning(request, duplicate_message)
                else:
                    messages.success(request, 'Фильм успешно добавлен в базу данных!')
            else:
                # Сохранение в файл
                save_film_data(film_data)
                messages.success(request, 'Фильм успешно добавлен в файл!')
            
            return redirect('film_add')
    else:
        films_form = FilmsForm()
    
    response = render(request, "film_add.html", {
        "films_form": films_form
    })
    return response

def save_film_to_database(data):
    """Сохраняет фильм в БД с проверкой на дубликаты. Возвращает сообщение о дубликате или None."""
    try:
        # Проверка на дубликат по title, director, country
        if Film.objects.filter(
            title=data['title'],
            director=data['director'],
            country=data['country']
        ).exists():
            return f'Фильм "{data["title"]}" с режиссёром "{data["director"]}" и страной "{data["country"]}" уже существует в базе данных.'
        
        Film.objects.create(**data)
        return None
    except Exception as e:
        return f'Ошибка при сохранении: {str(e)}'

def save_film_data(data):
    folder_path = os.path.join(settings.BASE_DIR, 'Films')
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, 'films.json')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)

    with open(file_path, 'r+', encoding='utf-8') as f:
        try:
            films = json.load(f)
        except json.JSONDecodeError:
            films = []
        films.append(data)
        f.seek(0)
        json.dump(films, f, ensure_ascii=False, indent=4)
        f.truncate()

def save_file_metadata(filename, original_name, title, size):
    metadata_file = os.path.join(settings.MEDIA_ROOT, 'file_metadata.json')
    # Загружаем существующие метаданные или создаем новый список
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                metadata = []
    else:
        metadata = []

    # Добавляем новую запись
    metadata.append({
        'id': len(metadata) + 1,
        'filename': filename,
        'original_name': original_name,
        'title': title,
        'size': size,
        'upload_date': datetime.now().isoformat()
    })

    # Перезаписываем файл метаданных
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_file_metadata():
    metadata_file = os.path.join(settings.MEDIA_ROOT, 'file_metadata.json')
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_file_data():
    folder_path = settings.MEDIA_ROOT
    data_list = []

    if not os.path.exists(folder_path):
        return []
    # Получаем информацию из JSON файлов для вывода
    for filename in os.listdir(folder_path):
        if filename.endswith('.json') and filename != 'file_metadata.json':
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        data_list.extend(content)
                    else:
                        data_list.append(content)
            except (json.JSONDecodeError, OSError):
                continue
    
    # Также читаем из Films/films.json
    films_file = os.path.join(settings.BASE_DIR, 'Films', 'films.json')
    if os.path.exists(films_file):
        try:
            with open(films_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, list):
                    data_list.extend(content)
                else:
                    data_list.append(content)
        except (json.JSONDecodeError, OSError):
            pass
    
    return data_list

# AJAX поиск
def film_search(request):
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        if query:
            films = Film.objects.filter(
                title__icontains=query
            ) | Film.objects.filter(
                genre__icontains=query
            ) | Film.objects.filter(
                director__icontains=query
            ) | Film.objects.filter(
                country__icontains=query
            )
        else:
            films = Film.objects.all()
        
        films_data = [{
            'id': film.id,
            'title': film.title,
            'genre': film.genre,
            'director': film.director,
            'country': film.country,
        } for film in films]
        
        return JsonResponse({'films': films_data})
    return JsonResponse({'films': []})

# Редактирование фильма
def film_edit(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    
    if request.method == 'POST':
        form = FilmEditForm(request.POST)
        if form.is_valid():
            # Проверка на дубликаты (исключая текущий фильм)
            title = form.cleaned_data['title']
            director = form.cleaned_data['director']
            country = form.cleaned_data['country']
            
            duplicate = Film.objects.filter(
                title=title,
                director=director,
                country=country
            ).exclude(id=film_id).exists()
            
            if duplicate:
                messages.error(request, f'Фильм с такими данными уже существует!')
                return render(request, 'film_edit.html', {
                    'form': form,
                    'film': film
                })
            
            film.title = title
            film.genre = form.cleaned_data['genre']
            film.director = director
            film.country = country
            film.save()
            messages.success(request, 'Фильм успешно обновлён!')
            from django.urls import reverse
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(reverse('film_list') + '?source=db')
    else:
        form = FilmEditForm(initial={
            'title': film.title,
            'genre': film.genre,
            'director': film.director,
            'country': film.country,
        })
    
    return render(request, 'film_edit.html', {
        'form': form,
        'film': film
    })

# Удаление фильма
def film_delete(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    
    if request.method == 'POST':
        film.delete()
        messages.success(request, 'Фильм успешно удалён!')
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('film_list') + '?source=db')
    
    return render(request, 'film_delete.html', {
        'film': film
    })
