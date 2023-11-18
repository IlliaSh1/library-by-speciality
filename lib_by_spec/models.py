from django.db import models


# Create your models here.

from book_parser.models import Book
from django.utils import timezone


class Favorite_book(models.Model):
    user = models.ForeignKey("users.User", verbose_name=("Пользователь"), on_delete=models.CASCADE)
    book = models.ForeignKey(
        "book_parser.Book", 
        verbose_name=("Книга"), 
        on_delete=models.CASCADE,
    )

    time_added = models.DateTimeField(
        verbose_name="Время добаления",
        default=timezone.now(),
    )
    
    def __str__(self):
        return "User: "+self.user.username+", Book: "+self.book.name 
    
    class Meta:
        verbose_name = "Избранная книга"
        verbose_name_plural = "Избранные книги"


