from django.contrib import admin

# Register your models here.


from .models import Book, Author
from discipline_selection.models import Discipline
from discipline_selection. models import Discipline

# Export from admin panel
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from import_export.fields import Field
from import_export.widgets import ManyToManyWidget


# Book
## Resource for exporting books.
class BookResource(resources.ModelResource):
    # link = Field()
    # name = Field()
    # cover = Field()
    # annotation = Field()
    # bibl_record = Field()
    # year_published = Field()
    # pages_count = Field()
    # isbn = Field()
    
    authors = Field(
        widget=ManyToManyWidget(model=Author, field='fullname'),
    )
    disciplines = Field(
        widget=ManyToManyWidget(model=Book, field='disciplines'),
    )
    
    class Meta:
        model = Book

    def dehydrate_authors(self, book):
        data = []
        for author in book.authors.all():
            data.append(author.fullname)
        joined_string = ", ".join(data)
        return str(joined_string)
    
    def dehydrate_disciplines(self, book):
        data = []
        for discipline in book.disciplines.all():
            data.append(discipline.name)
        joined_string = ", ".join(data)
        return str(joined_string)

    
@admin.register(Book)
class BookAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
    
    resource_class = BookResource

    # Custom method for exporting user favorite books.
    def get_export_queryset(self, request):
        # return super().get_export_queryset(request)
        user = request.user
        return user.favorite_books.all()

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
