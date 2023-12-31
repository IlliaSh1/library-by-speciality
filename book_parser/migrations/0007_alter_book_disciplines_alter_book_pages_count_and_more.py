# Generated by Django 4.2.2 on 2023-06-24 01:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discipline_selection', '0001_initial'),
        ('book_parser', '0006_alter_book_name_alter_discipline_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='disciplines',
            field=models.ManyToManyField(to='discipline_selection.discipline'),
        ),
        migrations.AlterField(
            model_name='book',
            name='pages_count',
            field=models.IntegerField(null=True, verbose_name='pages'),
        ),
        migrations.AlterField(
            model_name='book',
            name='year_published',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999)], verbose_name='year'),
        ),
        migrations.DeleteModel(
            name='Discipline',
        ),
        migrations.DeleteModel(
            name='Keyword',
        ),
    ]
