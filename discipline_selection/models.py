from django.db import models

# Create your models here.

from django.contrib import admin

class Keyword(models.Model):
    key_phrase = models.CharField(
        max_length=128, 
        verbose_name="Ключевая фраза",
        unique=True)
    
    def __str__(self):
        return self.key_phrase
    
    class Meta:
        verbose_name = "Ключевое слово"
        verbose_name_plural = "Ключевые слова"
    
class Discipline(models.Model):
    keywords = models.ManyToManyField(
        Keyword, 
        verbose_name="Ключевые слова"
    )
    
    name = models.CharField(
        max_length=256, 
        verbose_name="Название дисциплины",
        unique=True,
    )

    def __str__(self):
        return self.name
    
    @admin.display(
            description="Все ключевые слова",
    )
    def keywords_get_all(self):
        return ", ".join([k.key_phrase for k in self.keywords.all()])
    
    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
