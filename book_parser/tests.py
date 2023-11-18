from django.test import TestCase

# Create your tests here.

from .models import *

class BookDisciplineModelsTests(TestCase):
    def test_book_does_not_have_2_similar_discipline(self):
        """
        Must return false, because book mustn't have 1 discipline 2 times    
        """
        book = Book.objects.create(name = "Программирование на Python")
        backend_dev = Discipline.objects.create(name = "Основы серверной веб-разрботки", )

        book.disciplines.add(backend_dev)
        book.disciplines.add(backend_dev)
        self.assertIs(book.disciplines.all().count(), 1 )
