from django.db import models

# Create your models here.

from django.utils import timezone
from django.core.validators import MaxValueValidator

from django.contrib import admin

from discipline_selection.models import Discipline
from django.contrib.auth.models import AnonymousUser

# History
from simple_history.models import HistoricalRecords

class Author(models.Model):
    fullname = models.CharField(
        verbose_name="ФИО",
        max_length=128, 
        unique=True,
    )
    
    def __str__(self):
        return self.fullname
    
    def book_count(self):
        return self.book_set.all().count()

    book_count.short_description = "Написано книг"

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"


class Book(models.Model):

    link = models.URLField(
        verbose_name="Ссылка",
        null=True, 
        max_length=200,
        unique=True,
    )

    name = models.CharField(
        verbose_name="Название",
        max_length = 256, 
    )

    cover = models.ImageField(
        max_length=150,
        verbose_name="Обложка книги",
        null=True,
        upload_to=('covers/')
    )

    annotation = models.CharField(
        verbose_name="Аннотация",
        null = True, max_length=4096
    )
    bibl_record = models.CharField(
        verbose_name="Библиографическая запись",
        null = True, 
        max_length=2048,
    )

    year_published = models.PositiveIntegerField(
        verbose_name="Год",
        null = True,
        validators = [
            MaxValueValidator(9999)
        ],
    )
    pages_count = models.IntegerField(
        verbose_name="Страниц",
        null = True,
    )

    isbn = models.CharField(
        verbose_name="ISBN",
        null = True,
        max_length=64,
    )
    

    authors = models.ManyToManyField(
        Author,
        verbose_name="Авторы",
    )
    disciplines = models.ManyToManyField(
        Discipline,
        verbose_name="Дисциплины",
    )

    list_per_page = 50
    
    history = HistoricalRecords() 

    def __str__(self):
        return self.name
    

    @admin.display(
        description="Дисциплины"
    )
    def disciplines_get_all(self):
        return ", ".join([d.name for d in self.disciplines.all()])
    
    @admin.display(
        description="Авторы"
    )
    def authors_get_all(self):
        return ", ".join([a.fullname for a in self.authors.all()])
    
    @admin.display(
        description="В избранных",
    )
    def in_favorites_count(self):
        return self.user_set.all().count()
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


    
    
    
    

