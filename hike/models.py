from django.db import models
from PIL import Image
from django.db import models
from django.urls import reverse

SEASONS = [('теплое время года', 'теплое время года'),('лето','лето'), ('зима','зима'), ('весна','весна'), ('осень','осень')] 
TYPE = [('путешествия', 'путешествия'),('книги','книги'), ('фильмы','фильмы'), ('музеи','музеи'), ('учебные курсы','учебные курсы'), ('рецепты','рецепты'), ('покупки','покупки'), 
        ('фотоальбом','фотоальбом'), ('прогулка','прогулка'), ('поездка на выходные','поездка на выходные'), ('аудио','аудио'), ('работа','работа'),] 


class Hike(models.Model):
    how_long = models.IntegerField('Сколько дней',  blank=True, null=True, default='1')
    season = models.CharField('Сезон', max_length=10000, blank=True, choices=SEASONS, null=True, default='теплое время года')
    country = models.CharField('Страна', max_length=10000, blank=True, null=True, default='Россия')
    region = models.CharField('Регион', max_length=10000, blank=True, null=True, default='Северо-Запад')
    title = models.CharField('Заголовок', max_length=10000, blank=True, null=True)
    reality = models.BooleanField(verbose_name='Пройдено',
                                           blank=True, null=True, default=False)
    date = models.DateField('Дата добавления записи', auto_now_add=True, db_index=True)
    start_station = models.CharField('Вокзал отправления туда', max_length=10000, blank=True, null=True)
    aim_station = models.CharField('Вокзал прибытия туда', max_length=10000, blank=True, null=True)
    home_station = models.CharField('Вокзал прибытия оттуда', max_length=10000, blank=True, null=True)
    back_station = models.CharField('Вокзал отправления оттуда', max_length=10000, blank=True, null=True)
    travel_details = models.TextField('Подробности добирания и комментарии',  blank=True, null=True)
    attractions = models.TextField('Достопримечательности',  blank=True, null=True)
    kilometers = models.CharField('Примерный километраж', max_length=10000, blank=True, null=True)
    vk = models.CharField('Ссылка на встречу вк', max_length=10000, blank=True, null=True)
    track = models.CharField('Ссылка на трек', max_length=10000, blank=True, null=True)
    img_track_project = models.ImageField('Трек план', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
    img_track_fact = models.ImageField('Трек факт', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
    dates_try = models.CharField('Даты прохождения', max_length=10000, blank=True, null=True, default='в планах')
    maturity = models.BooleanField(verbose_name='Готов ли маршрут?',
                                           blank=True, null=True, default=False)


    
    
    def __str__(self):
        return f' {self.date} , {self.title}'

    class Meta:
        verbose_name = 'Хайкинг'
        verbose_name_plural = 'Хайкинг'


class Comments(models.Model):
    date = models.DateField('Дата', auto_now_add=True, db_index=True)
    text = models.TextField('Содержание', max_length=1000, default='')
    forNote = models.ForeignKey(Hike, verbose_name='К записи', on_delete=models.PROTECT,
                                related_name='comments')
    author = models.CharField('Автор', max_length=50)

    def __str__(self):
        return f' {self.author} , к {self.forNote.title},  от {self.date}'

    def get_absolute_url(self):
        """ Создание юрл объекта для перенаправления из вьюшки создания объекта на страничку с созданным объектом """
        return reverse('blogstr', kwargs={'pk': self.forNote.pk})

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pk']



class Bookmarks(models.Model):
    type = models.CharField('Раздел', max_length=10000, blank=True, choices=TYPE, null=True, default='путешествия')
    undertype = models.CharField('Подраздел', max_length=10000, blank=True, null=True)
    text = models.TextField('Текст', blank=True, null=True)
    country = models.CharField('Страна', max_length=10000, blank=True, null=True, default='Россия')
    region = models.CharField('Регион (город)', max_length=10000, blank=True, null=True, default='Любой')
    vk = models.CharField('Ссылка на источник', max_length=10000, blank=True, null=True)
    done = models.BooleanField(verbose_name='Использовано ли?', default=False, null=True)
                                   
    def __str__(self):
        return f' {self.type} , {self.region}'

    class Meta:
        verbose_name = 'Закладки по темам'
        verbose_name_plural = 'Закладки по темам'

class Itbookmarks(models.Model):
    type = models.CharField('Раздел', max_length=10000, blank=True,  null=True, default='любой')
    text = models.TextField('Текст', blank=True, null=True)
    vk = models.CharField('Ссылка', max_length=10000, blank=True, null=True)

    def __str__(self):
        return f'№ {self.pk} -  {self.type}'

    class Meta:
        verbose_name = 'Записная книжка по айти'
        verbose_name_plural = 'Записная книжка по айти'

class Kareliahistory(models.Model):
    title = models.CharField('Раздел', max_length=10000, blank=True,  null=True)
    text = models.TextField('Текст', blank=True, null=True)
    vk = models.CharField('Ссылка', max_length=10000, blank=True, null=True)

    def __str__(self):
        return f'№ {self.pk} .  {self.title}'

    class Meta:
        verbose_name = 'История Карелии'
        verbose_name_plural = 'История Карелии'



class Family(models.Model):
    type = models.CharField('Заголовок', max_length=10000, blank=True,  null=True, default='любой')
    text = models.TextField('Текст', blank=True, null=True)
    vk = models.CharField('Ссылка', max_length=10000, blank=True, null=True)
    photo = models.ImageField('Фото', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')

    def __str__(self):
        return f'№ {self.pk} -  {self.type}'

    class Meta:
        verbose_name = 'Закладки семья'
        verbose_name_plural = 'Закладки семья'


class Chemistry(models.Model):
    type = models.CharField('Заголовок', max_length=10000, blank=True,  null=True, default='любой')
    text = models.TextField('Текст', blank=True, null=True)
    vk = models.CharField('Ссылка', max_length=10000, blank=True, null=True)
    photo = models.ImageField('Фото', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')

    def __str__(self):
        return f'№ {self.pk} -  {self.type}'

    class Meta:
        verbose_name = 'Химия'
        verbose_name_plural = 'Химия'


CAT_H = [('-','-'), ('Воцарение правителя', 'Воцарение правителя'), ('Война', 'Война'), ('Территориальные изменения', 'Территориальные изменения'),] 
TYPE_H = [('История','История'), ('Культура', 'Культура'),] 
REGION = [('Северо-Западный регион','Северо-Западный регион'),('Россия', 'Россия'), ('Европа', 'Европа'), ('Азия', 'Азия'), ('США', 'США'),] 


class History(models.Model):
    century = models.IntegerField('Век',  blank=True, null=True, default='1')
    year = models.IntegerField('Год начала',  blank=True, null=True, default='800')
    region = models.CharField('Регион', max_length=10000, blank=True, choices=REGION, null=True, default='Россия')
    type = models.CharField('Тип', max_length=10000, blank=True, choices=TYPE_H, null=True, default='История')
    cat = models.CharField('Категория', max_length=10000, blank=True, choices=CAT_H, null=True, default='-')
    title = models.CharField('Заголовок', max_length=10000, blank=True, null=True)
    text = models.TextField('Текст', blank=True, null=True)
    text_long = models.TextField('Подробности и ссылки', blank=True, null=True)
    photo1 = models.ImageField('Иллюстрация1', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
    photo2 = models.ImageField('Иллюстрация2', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
    photo3 = models.ImageField('Иллюстрация3', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
    photo4 = models.ImageField('Иллюстрация4', upload_to='user_images', blank=True, null=True,
                                        default='user_images/default1.png')
        
  
    def __str__(self):
        return f'{self.century} ,{self.region} , {self.year} , {self.title}'

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'Историческая картина мира'
