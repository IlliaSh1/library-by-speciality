# Generated by Django 4.2.2 on 2023-06-25 14:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0018_alter_favorite_book_time_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite_book',
            name='time_added',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 25, 14, 56, 29, 557514, tzinfo=datetime.timezone.utc), verbose_name='Время добаления'),
        ),
    ]
