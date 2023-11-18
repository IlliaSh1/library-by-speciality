from django.contrib import admin

# Register your models here.


from .models import Book, Author
from discipline_selection. models import Discipline

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", ("link","cover"), ("year_published", "pages_count")]}),
        ("Описание книги", {"fields": ["annotation", "bibl_record"]}),
        ("Идентификаторы книги", {"fields": ["id", "isbn"]}),
        ("Дисциплины", {"fields": ["disciplines"]}),
        ("Авторы", {"fields": ["authors"]}),
    ]

    list_display = ['name', 'year_published', 'pages_count', 
                    'disciplines_get_all', 'isbn', 
                    'authors_get_all', 'in_favorites_count']

    list_filter = ['year_published', 'disciplines']

    filter_horizontal = ['disciplines']


    raw_id_fields = ['authors']
    readonly_fields = ["id"]

    ordering = ["-year_published", "name"]

    search_fields = ['name']

    list_per_page = 100
    



# Author
class BookAuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 3
    raw_id_fields = ['book']
    verbose_name = "Книга"
    verbose_name_plural = "Книги"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["fullname"]}),
    ]
    list_display = ["fullname", "book_count"]

    # filter_horizontal = "books"
    inlines = [BookAuthorInline]

    ordering = ["fullname"]
    

# Inlines

class BookDisciplineInline(admin.TabularInline):
    model = Book.disciplines.through
    raw_id_fields = ["book",]
    extra = 3
    verbose_name="Книга",
    verbose_name_plural="Книги"
