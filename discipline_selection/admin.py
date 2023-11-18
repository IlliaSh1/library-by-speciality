from django.contrib import admin

# Register your models here.

from .models import Discipline, Keyword

from book_parser.admin import BookDisciplineInline

# Discipline
@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Ключевые фразы для отбора", {"fields": ["keywords"]}),
    ]

    list_display = ['name']
    raw_id_fields = ["keywords"]
    inlines = [BookDisciplineInline]

    ordering = ["name"]

    search_fields = ['name']

# Keyword
class DisciplineKeywordInline(admin.TabularInline):
    model = Discipline.keywords.through
    # verbose_name = ""
    verbose_name_plural = "Disciplines with this keyword"
    extra = 2

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["key_phrase"]}),
    ]
    list_display = ['id', 'key_phrase']

    list_display_links = ['id', 'key_phrase']

    inlines = [DisciplineKeywordInline]
    
    search_fields = ['key_phrase']

    ordering = ["id"]