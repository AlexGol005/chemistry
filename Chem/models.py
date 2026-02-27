from django.db import models
from django.urls import reverse
from django.conf import settings
from PIL import Image
from django.core.exceptions import ValidationError
from rdkit import Chem as Chemrdkit

LEVEL = [
        ('ОГЭ', 'ОГЭ'),
        ('ЕГЭ', 'ЕГЭ'),
    ]

ORGANIC_CLASSES = [
    ('alkanes', 'Алканы'),
    ('alkenes', 'Алкены'),
    ('alkynes', 'Алкины'),
    ('alkadienes', 'Алкадиены'),
    ('cycloalkanes', 'Циклоалканы'),
    ('arenes', 'Арены'),
    ('alcohols', 'Спирты'),
    ('phenols', 'Фенолы'),
    ('ethers', 'Простые эфиры'),
    ('aldehydes', 'Альдегиды'),
    ('ketones', 'Кетоны'),
    ('carboxylic_acids', 'Карбоновые кислоты'),
    ('esters', 'Сложные эфиры'),
    ('fats', 'Жиры'),
    ('carbohydrates', 'Углеводы'),
    ('amines', 'Амины'),
    ('nitro_compounds', 'Нитросоединения'),
    ('amino_acids', 'Аминокислоты'),
    ('proteins', 'Белки'),
    ('nucleic_acids', 'Нуклеиновые кислоты'),
    ('halogen_derivatives', 'Галогенопроизводные'),
    ('thiols', 'Тиолы'),
    ('heterocycles', 'Гетероциклы'),
    ('organometallic_compounds', 'Элементоорганические соединения'),
    ('inorganic_compounds', 'Неорганические соединения'),
] 


class OrganicNames(models.Model): # Используем стандартный models.Model
    name1 = models.CharField('Название 1', max_length=255, blank=True, null=True, unique=True)
    name2 = models.CharField('Название 2', max_length=255, blank=True, null=True, unique=True)
    name3 = models.CharField('Название 3', max_length=255, blank=True, null=True, unique=True)
    name4 = models.CharField('Название 4', max_length=255, blank=True, null=True, unique=True)
    formula = models.CharField('Молекулярная формула', max_length=10000, blank=True, null=True, unique=True)
    molecule = models.TextField('Структурная формула', null=True, blank=True)
    molecule_short = models.TextField('сокращенная структурная формула', null=True, blank=True)
    appearance = models.TextField('Внешний вид', blank=True, null=True) 
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)
    organic_class = models.CharField('Класс', blank=True, null=True, default='ЕГЭ', choices=ORGANIC_CLASSES)

    @property
    def mol_object(self):
        """Метод для получения объекта RDKit из строки SMILES"""
        if self.molecule:
            return Chemrdkit.MolFromSmiles(self.molecule)
        return None

        def __str__(self):
            # Вместо return self.name (где name может быть None)
            return str(self.name1) if self.name1 else "Без названия"

    def clean(self):
        # Ищем существующую запись с такими же полями
        duplicate = OrganicNames.objects.filter(name1=self.name1).exclude(pk=self.pk).first()
        
        if duplicate:
            # Выбрасываем ошибку с PK дубликата
            raise ValidationError(
                f"Ошибка! Место уже занято. Дублирующая запись имеет ID: {duplicate.pk}"
            )
        super().clean()    

    class Meta:
        verbose_name = "Органическое соединение"
        verbose_name_plural = "Органические соединения"


class Organiclaw(models.Model):
    """ Законы органической химии """
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.IntegerField('Номер закона', blank=True, null=True)
    title = models.TextField('Заголовок', blank=True, null=True)
    text = models.TextField('Описание закона', blank=True, null=True)
    trening = models.TextField('Ссылки', blank=True, null=True)
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)
    presentation = models.FileField(upload_to='presentations/', verbose_name="Файл презентации", blank=True, null=True)
                                        


    def __str__(self):
        count = self.organicreaction_set.count()
        return f'{self.title} - {count} реакций'


    class Meta:
        verbose_name = 'Закон органической химии'
        verbose_name_plural = 'Законы органической химии'


class OrganicReaction(models.Model):
    """ Реакции органической химии """
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.ForeignKey(Organiclaw,  on_delete=models.PROTECT,
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
    level = models.CharField('Уровень', blank=True, null=True, default='ЕГЭ', choices=LEVEL)
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)

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
        verbose_name = 'Реакция органической химии'
        verbose_name_plural = 'Реакции органической химии'

    def clean(self):
        # Ищем существующую запись с такими же полями
        duplicate = OrganicReaction.objects.filter(reagent1=self.reagent1, reagent2=self.reagent2, reagent3=self.reagent3, condition=self.condition, number=self.number,).exclude(pk=self.pk).first()
        
        if duplicate:
            # Выбрасываем ошибку с PK дубликата
            raise ValidationError(
                f"Ошибка! Место уже занято. Дублирующая запись имеет ID: {duplicate.pk}"
            )
        super().clean()




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
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)
    presentation = models.FileField(upload_to='presentations/', verbose_name="Файл презентации", blank=True, null=True)
                                        


    def __str__(self):
        count = self.inorganicreaction_set.count()
        return f'{self.title} - {count} реакций'


    class Meta:
        verbose_name = 'Закон неорганической химии'
        verbose_name_plural = 'Законы неорганической химии'


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
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)

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
    """ Названия веществ неорганических """
    date = models.DateField('Дата', auto_now_add=True)
    formula = models.CharField('Формула', max_length=10000, blank=True, null=True, unique=True)
    name = models.TextField('Все названия этого соединения', blank=True, null=True)    
    appearance = models.TextField('Внешний вид', blank=True, null=True) 
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)

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
    """ Законы общей химии """
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
    presentation = models.FileField(upload_to='presentations/', verbose_name="Файл презентации", blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)

    @property
    def file_extension(self):
        return os.path.splitext(self.presentation.name)[1].lower()

    def __str__(self):
        if self.title:
            return f'{self.pk} - {self.title}'
        return f'{self.pk}'

    class Meta:
        verbose_name = 'Закон строения атомов и периодичности'
        verbose_name_plural = 'Законы строения атомов и периодичности'


class AtomTest(models.Model):
    """ Законы общей химии - вопросы """
    date = models.DateField('Дата', auto_now_add=True)
    metatitle = models.CharField('Метазаголовок страницы', max_length=10000, blank=True, null=True)
    description = models.TextField('Метаописание страницы', blank=True, null=True)    
    keywords = models.TextField('Ключевые слова', blank=True, null=True)
    
    number = models.ForeignKey(Atomlaw,  on_delete=models.PROTECT,
                                   verbose_name='Закон', blank=True, null=True, default=1)
    
    text = models.TextField('Вопрос', blank=True, null=True)
    answer = models.TextField('Ответ', blank=True, null=True)
    level = models.CharField('Уровень', blank=True, null=True, default='ЕГЭ', choices=LEVEL)
    img1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True)
                                        
    img2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True)
                                      
    img3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True)
    video = models.CharField('Видео', max_length=10000, blank=True, null=True)

    def __str__(self):
        if self.metatitle:
            return f'{self.pk} - {self.metatitle}'
        return f'{self.pk}'
    
    class Meta:
        verbose_name = 'Вопросы к разделу: законы строения атомов и периодичности'
        verbose_name_plural = 'Вопросы к разделу: законы строения атомов и периодичности'


class Table(models.Model):
    """ Таблицы по химии """
    img = models.ImageField('таблица', upload_to='user_images', blank=True, null=True)



    def __str__(self):
        return f'{self.pk}'
    
    class Meta:
        verbose_name = 'Таблица по химии'
        verbose_name_plural = 'Таблицы по химии'
        

class Link(models.Model):
    """ Полезные ссылки """
    type = models.TextField('Тип', blank=True, null=True)
    title = models.TextField('Заголовок', blank=True, null=True)
    text = models.TextField('Ссылка', blank=True, null=True)



    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name = 'Ссылка по химии'
        verbose_name_plural = 'Ссылки по химии'


class UserReaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_reactions')
    reaction = models.ForeignKey(InorganicReaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reaction') # Защита от дублей

class OrganicUserReaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organic_favorite_reactions')
    reaction = models.ForeignKey(OrganicReaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reaction') # Защита от дублей






