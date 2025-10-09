from django.db import models
from django.urls import reverse


class Inorganiclaw(models.Model):
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)
    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.TextField('Номер закона')
    title = models.TextField('Заголовок')
    text = models.TextField('Описание закона')
    formula = models.TextField('Общая формула закона')
    examples = models.TextField('Примеры')
    exceptions = models.TextField('Описание исключений')
    trening = models.TextField('Тренировка')




    def __str__(self):
        return f' {self.date} , {self.title}'

    class Meta:
        verbose_name = 'Закон неорганической химии'
        verbose_name_plural = 'Законы неорганической химии'
