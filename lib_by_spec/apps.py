from django.apps import AppConfig

from django.apps import AppConfig


class LibBySpecConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lib_by_spec'
    verbose_name = "Избранные книги пользователей"