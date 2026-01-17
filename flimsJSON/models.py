from django.db import models

class Film(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название фильма")
    genre = models.CharField(max_length=30, verbose_name="Жанр")
    director = models.CharField(max_length=100, verbose_name="Режиссёр")
    country = models.CharField(max_length=50, verbose_name="Страна производства")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ['-created_at']
        unique_together = [['title', 'director', 'country']]
    
    def __str__(self):
        return self.title
