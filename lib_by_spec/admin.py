from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html

from .models import Favorite_book
from users.models import User

@admin.register(Favorite_book)
class Favorite_bookAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": [
                'user', 'book'
            ],

        }),
        ("Time added", {
            "fields": [
                'time_added'
            ]
        })
    )

    list_display = ["user", "book", 'time_added' ]
    
    list_filter = ["user"]

    list_display_links = ['user', 'book']

    ordering = ["-time_added"]
    
    date_hierarchy = "time_added"

    search_fields = ["user__username", "book__name"]

    


class Favorite_bookInline(admin.TabularInline):
    model = Favorite_book
    raw_id_fields = ["book"]
    extra = 3