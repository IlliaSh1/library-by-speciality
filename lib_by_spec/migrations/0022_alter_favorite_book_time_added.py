# Generated by Django 4.2.7 on 2023-11-18 22:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0021_alter_favorite_book_time_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite_book',
            name='time_added',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 18, 22, 6, 11, 481192, tzinfo=datetime.timezone.utc), verbose_name='Время добаления'),
        ),
    ]
