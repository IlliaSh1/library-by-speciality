# Generated by Django 4.2.2 on 2023-06-23 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0004_alter_favorite_book_time_added'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favorite_book',
            name='time_added',
        ),
    ]
