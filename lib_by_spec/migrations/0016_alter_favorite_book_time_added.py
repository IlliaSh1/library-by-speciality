# Generated by Django 4.2.2 on 2023-06-24 01:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0015_alter_favorite_book_time_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite_book',
            name='time_added',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 24, 1, 23, 4, 212838, tzinfo=datetime.timezone.utc)),
        ),
    ]