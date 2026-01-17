# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название фильма')),
                ('genre', models.CharField(max_length=30, verbose_name='Жанр')),
                ('director', models.CharField(max_length=100, verbose_name='Режиссёр')),
                ('country', models.CharField(max_length=50, verbose_name='Страна производства')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
                'ordering': ['-created_at'],
                'unique_together': {('title', 'director', 'country')},
            },
        ),
    ]

