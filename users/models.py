from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.utils import timezone

from book_parser.models import Book
from lib_by_spec.models import Favorite_book

class User(AbstractUser):
    favorite_books = models.ManyToManyField(
        "book_parser.Book", 
        verbose_name="Книга",   
        through="lib_by_spec.Favorite_book",
    )
