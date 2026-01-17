from django.contrib import admin
from .models import Film

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'director', 'country', 'created_at')
    list_filter = ('genre', 'country', 'created_at')
    search_fields = ('title', 'director', 'country')
