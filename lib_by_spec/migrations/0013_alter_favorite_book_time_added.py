# Generated by Django 4.2.2 on 2023-06-23 20:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0012_alter_favorite_book_time_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite_book',
            name='time_added',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 23, 20, 7, 8, 337000, tzinfo=datetime.timezone.utc)),
        ),
    ]
