# Generated by Django 4.2.2 on 2023-06-22 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_parser', '0003_keyword'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorite_books',
            field=models.ManyToManyField(to='book_parser.book'),
        ),
    ]
