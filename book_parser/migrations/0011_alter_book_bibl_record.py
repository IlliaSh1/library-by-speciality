# Generated by Django 4.2.2 on 2023-06-25 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_parser', '0010_alter_book_annotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='bibl_record',
            field=models.CharField(max_length=2048, null=True, verbose_name='Библиографическая запись'),
        ),
    ]