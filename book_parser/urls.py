from django.urls import path

from . import views

app_name = "book_parser"
urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name="results"),
    path("processing/", views.processing, name="processing"),
    path("start_parse/", views.parse_start, name="start_parse"),
    
    path("books/", views.BookListApiView.as_view(), name="parsed_books_api"),
    path("books/<int:pk>", views.BookDetailApiView.as_view(), name="parsed_book_api"),
]
