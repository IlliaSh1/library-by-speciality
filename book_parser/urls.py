from django.urls import path, include

from . import views
from rest_framework import routers 

router  = routers.DefaultRouter()
router.register('books', views.BookApiView)
router.register('authors', views.AuthorApiView)
router.register('book_list', views.BookApiView)


app_name = "book_parser"
urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name="results"),
    path("processing/", views.processing, name="processing"),
    path("start_parse/", views.parse_start, name="start_parse"),
    
    # path("book_list/", views.BookListApiView.as_view(), name="parsed_books_api"),
    path("book_list/<int:pk>", views.BookDetailApiView.as_view(), name="parsed_book_api"),
    path("api/v1/", include(router.urls))
]