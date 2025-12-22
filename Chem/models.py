from django.db import models
from django.urls import reverse
from PIL import Image


class Inorganiclaw(models.Model):
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.IntegerField('Номер закона', blank=True, null=True)
    title = models.TextField('Заголовок', blank=True, null=True)
    text = models.TextField('Описание закона', blank=True, null=True)
    formula = models.TextField('Общая формула закона', blank=True, null=True)
    examples = models.TextField('Примеры', blank=True, null=True)
    exceptions = models.TextField('Описание исключений', blank=True, null=True)
    trening = models.TextField('Тренировка', blank=True, null=True)
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
                                        


    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Закон неорганической химии'
        verbose_name_plural = 'Законы неорганической химии'



class InorganicReaction(models.Model):
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.ForeignKey(Inorganiclaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True, related_name='n1')

    number2 = models.ForeignKey(Inorganiclaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True, related_name='n2')
    number3 = models.ForeignKey(Inorganiclaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True, related_name='n3')
    
    reagent1 = models.CharField('Реагент1', blank=True, null=True)
    reagent2 = models.CharField('Реагент2', blank=True, null=True)
    reagent3 = models.CharField('Реагент3', blank=True, null=True)

    product1 = models.CharField('Продукт1', blank=True, null=True)
    product2 = models.CharField('Продукт1', blank=True, null=True)
    product3 = models.CharField('Продукт1', blank=True, null=True)
    product4 = models.CharField('Продукт1', blank=True, null=True)

    def __str__(self):
        return f'{self.number.title} - {self.metatitle}'

    class Meta:
        verbose_name = 'Реакция неорганической химии'
        verbose_name_plural = 'Реакции неорганической химии' 

