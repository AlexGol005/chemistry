from django.db import models
from django.urls import reverse
from PIL import Image
from django.core.exceptions import ValidationError


class Inorganiclaw(models.Model):
    """ Законы неорганической химии """
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
        count = self.inorganicreaction_set.count()
        return f'{self.title} - {count} реакций'


    class Meta:
        verbose_name = 'Закон неорганической химии'
        verbose_name_plural = 'Законы неорганической химии'

LEVEL = [
        ('ОГЭ', 'ОГЭ'),
        ('ЕГЭ', 'ЕГЭ'),
    ]

class InorganicReaction(models.Model):
    """ Реакции неорганической химии """
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.ForeignKey(Inorganiclaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True)
    
    reagent1 = models.CharField('Реагент1', blank=True, null=True)
    reagent2 = models.CharField('Реагент2', blank=True, null=True)
    reagent3 = models.CharField('Реагент3', blank=True, null=True)

    condition = models.CharField('Условия реакции', blank=True, null=True, default='нормальные условия')

    product1 = models.CharField('Продукт1', blank=True, null=True)
    product2 = models.CharField('Продукт1', blank=True, null=True)
    product3 = models.CharField('Продукт1', blank=True, null=True)
    product4 = models.CharField('Продукт1', blank=True, null=True)
    
    video = models.CharField('Ссылка на видео', blank=True, null=True)
    extra = models.CharField('Дополнительная информация', blank=True, null=True)
    level = models.CharField('Уровень', blank=True, null=True, default='ОГЭ', choices=LEVEL)

    def __str__(self):
        try:
            return f'pk={self.pk}. {self.reagent1} + {self.reagent2}  (({self.number.title} - {self.metatitle})'
        except:
            try:
                return f'pk={self.pk}. {self.reagent1} + {self.reagent2}  ?? - {self.metatitle})'
            except:
                return  f'pk={self.pk}. Не указано!'

    class Meta:
        unique_together = ['reagent1', 'reagent2', 'reagent3', 'condition', 'number']
        verbose_name = 'Реакция неорганической химии'
        verbose_name_plural = 'Реакции неорганической химии'

    def clean(self):
        # Ищем существующую запись с такими же полями
        duplicate = InorganicReaction.objects.filter(reagent1=self.reagent1, reagent2=self.reagent2, reagent3=self.reagent3, condition=self.condition, number=self.number,).exclude(pk=self.pk).first()
        
        if duplicate:
            # Выбрасываем ошибку с PK дубликата
            raise ValidationError(
                f"Ошибка! Место уже занято. Дублирующая запись имеет ID: {duplicate.pk}"
            )
        super().clean()


class NamesCompaunds(models.Model):
    """ Названия веществ """
    date = models.DateField('Дата', auto_now_add=True)
    formula = models.CharField('Формула', max_length=10000, blank=True, null=True, unique=True)
    name = models.TextField('Все названия этого соединения', blank=True, null=True)    
    appearance = models.TextField('Внешний вид', blank=True, null=True) 

    class Meta:
        verbose_name = 'Название химического вещества'
        verbose_name_plural = 'Названия химических веществ'

    def clean(self):
        # Ищем существующую запись с такими же полями
        duplicate = NamesCompaunds.objects.filter(formula=self.formula).exclude(pk=self.pk).first()
        
        if duplicate:
            # Выбрасываем ошибку с PK дубликата
            raise ValidationError(
                f"Ошибка! Место уже занято. Дублирующая запись имеет ID: {duplicate.pk}"
            )
        super().clean()


class Atomlaw(models.Model):
    """ Законы строения атомов """
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

class AtomTest(models.Model):
    """ Законы строения атомов - вопросы """
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.ForeignKey(Atomlaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True, default=1)
    
    text = models.CharField('Вопрос', blank=True, null=True)
    answer = models.CharField('Ответ', blank=True, null=True)

