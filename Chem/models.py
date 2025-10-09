from django.db import models
from django.urls import reverse


class Chem(models.Model):
    date = models.DateField('Дата', auto_now_add=True)
    title = models.CharField('Заголовок', max_length=10000)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    text = models.TextField('Текст записи.')




    def __str__(self):
        return f' {self.date} , {self.title}'

    class Meta:
        verbose_name = 'Закон неорганической химии'
        verbose_name_plural = 'Законы неорганической химии'
