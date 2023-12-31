# Generated by Django 4.2.2 on 2023-06-25 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_by_spec', '0017_alter_favorite_book_options_alter_favorite_book_book_and_more'),
        ('book_parser', '0008_alter_author_options_alter_book_options_and_more'),
        ('users', '0008_remove_user_time_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='favorite_books',
            field=models.ManyToManyField(through='lib_by_spec.Favorite_book', to='book_parser.book', verbose_name='Книга'),
        ),
    ]
