# Generated by Django 4.2.2 on 2023-06-25 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_parser', '0009_book_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='annotation',
            field=models.CharField(max_length=4096, null=True, verbose_name='Аннотация'),
        ),
    ]
