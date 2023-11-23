from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
# Register your models here.

from lib_by_spec.admin import Favorite_bookInline

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    
    list_display = ('id',)+UserAdmin.list_display+('last_login', 'date_joined')
    # list_filter = UserAdmin.list_filter+('time_created',)
    
    inlines = [Favorite_bookInline]
    
    list_display_links = ['username']
    # raw_id_fields = UserAdmin.raw_id_fields+('favorite_books',)

    # ordering = ('-last_login',)+UserAdmin.ordering

