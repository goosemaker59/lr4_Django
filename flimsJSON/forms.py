from django import forms

class FilmsForm(forms.Form):
    STORAGE_CHOICES = [
        ('file', 'Файл (JSON)'),
        ('database', 'База данных'),
    ]
    
    title = forms.CharField(
        max_length=100, 
        label="Название фильма",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    genre = forms.CharField(
        max_length=30, 
        label="Жанр",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    director = forms.CharField(
        max_length=100, 
        label="Режиссёр",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        max_length=50, 
        label="Страна производства",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    storage_type = forms.ChoiceField(
        choices=STORAGE_CHOICES,
        label="Куда сохранить",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='file'
    )

class FilmEditForm(forms.Form):
    """Форма для редактирования фильма без поля storage_type"""
    title = forms.CharField(
        max_length=100, 
        label="Название фильма",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    genre = forms.CharField(
        max_length=30, 
        label="Жанр",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    director = forms.CharField(
        max_length=100, 
        label="Режиссёр",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        max_length=50, 
        label="Страна производства",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class FileForm(forms.Form):
    title = forms.CharField(
        max_length=100, 
        label="Название файла",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    file = forms.FileField(
        label="Импорт файла",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.json'):
                raise forms.ValidationError("Разрешены только файлы с расширением .json.")
        return file
