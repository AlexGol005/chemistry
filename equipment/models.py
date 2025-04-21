"""
Модуль проекта LabJournal, приложения equipment.
Приложение equipment это обширное приложение, включает все про лабораторное оборудование и лабораторные помещения
Данный модуль models.py выводит классы, создающие таблицы в базе данных - далее: модели.
Список блоков:
блок 1 - константы
блок 2 -  производители и поверители, комнаты лаборатории
блок 3 - оборудование в целом, характеристики СИ ИО ВО, сами СИ ИО ВО
блок 4 - смена комнаты, ответственного, добавление принадлежностей к оборудованию
блок 5 - поверка СИ, аттестация ИО, проверка характеристик ВО
блок 6 - комментарии
блок 7 - микроклимат в помещении
блок 8 - техобслуживание
блок 9 - отправка в поверку
"""
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image
from django.contrib.auth.models import User
from decimal import *
from django.urls import reverse
from django_currentuser.db.models import CurrentUserField

from users.models import  Company
from functstandart import get_dateformat

# блок 1 - константы неизменяемые непользовательские константы для полей с выбором значений в моделях

CHOICES = (
        ('Э', 'Экс.'),
        ('РЕ', 'Рем.'),
        ('С', 'Сп.'),
        ('Р', 'Рез.'),
        ('Д', 'Др.'),
    )

KATEGORY = (
        ('СИ', 'Средство измерения'),
        ('ИО', 'Испытательное оборудование'),
        ('ВО', 'Вспомогательное оборудование'),
    )

NOTETYPE = (
        ('Техническое обслуживание', 'Техническое обслуживание'),
        ('Неисправность', 'Неисправность'),
        ('Ремонт', 'Ремонт'),
        ('Другое', 'Другое'),
    )

CHOICESVERIFIC = (
        ('Поверен', 'Поверен'),
        ('Признан непригодным', 'Признан непригодным'),
        ('Спорный', 'Спорный'),
    )

CHOICESCAL = (
        ('Калиброван', 'Калиброван'),
        ('Признан непригодным', 'Признан непригодным'),
        ('Спорный', 'Спорный'),
    )

CHOICESATT = (
        ('Аттестован', 'Аттестован'),
        ('Признан непригодным', 'Признан непригодным'),
        ('Спорный', 'Спорный'),
    )

CHOICESPLACE = (
        ('У поверителя', 'У поверителя'),
        ('На месте эксплуатации', 'На месте эксплуатации'),
    )

HAVE = (('собственность', 'собственность'),
                                     ('аренда', 'аренда'))



# блок 2 -  производители и поверители

class Manufacturer(models.Model):
    """Производители оборудования"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorman')
    updated_by = CurrentUserField(related_name='updatorman')
    companyName = models.CharField('Производитель', max_length=10000, unique=True)
    companyAdress = models.CharField('Адрес', max_length=20000, default='', blank=True)
    country = models.CharField('Страна', max_length=20000, default='Россия', blank=True)
    telnumber = models.CharField('Телефон', max_length=200, default='', blank=True)
    telnumberhelp = models.CharField('Телефон техподдержки для вопросов по оборудованию',
                                     max_length=200, default='', blank=True)
    pointer =  models.CharField('ID добавившей организации', max_length=500, blank=True, null=True)

    def __str__(self):
        return self.companyName

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super(Manufacturer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Контрагенты: Производитель'
        verbose_name_plural = 'Контрагенты: Производители'

class Test(models.Model):
    """тест"""
    text = models.CharField('Поверитель', max_length=100)



class Verificators(models.Model):
    """Компании поверители оборудования"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatororgver', editable=True)
    updated_by = CurrentUserField(related_name='updatororgver', editable=True)
    companyName = models.CharField('Поверитель', max_length=100, unique=True)
    companyAdress = models.CharField('Адрес', max_length=200, default='-', blank=True)
    telnumber = models.CharField('Телефон', max_length=200, default='-', blank=True)
    email = models.CharField('email', max_length=200, default='-', blank=True)
    note = models.CharField('Примечание', max_length=10000, default='-', blank=True)
    head_position = models.CharField('Кому: должность лица организации-поверителя', max_length=100, default=None, null=True, blank=True)
    head_name = models.CharField('Кому: имя лица организации-поверителя', max_length=100, default=None, null=True, blank=True)
    pointer =  models.CharField('ID добавившей организации', max_length=500, blank=True, null=True, default=None,)

    def __str__(self):
        return f'{self.companyName}'

    def save(self, *args, **kwargs):
            if not self.pointer:
                    self.pointer = self.created_by.profile.userid
            super(Verificators, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Контрагенты: Поверитель'
        verbose_name_plural = 'Контрагенты: Поверители'


# блок 3 - оборудование в целом, характеристики СИ ИО ВО, сами СИ ИО ВО

class Equipment(models.Model):
    """Лабораторное оборудование - базовая индивидуальная сущность"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatoreq', editable=True)
    updated_by = CurrentUserField(related_name='updatoreq', editable=True)        
    date = models.DateField('Дата внесения записи', auto_now_add=True, blank=True, null=True) 
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True) 
    exnumber = models.CharField('Внутренний номер', max_length=100, default='', blank=True, null=True)

        
    lot = models.CharField('Заводской номер', max_length=10000, default='')
    yearmanuf = models.IntegerField('Год выпуска', default=0, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name='Название компании-производителя')
    new = models.CharField('Новый или б/у (указать: "новый" или "б/у")', max_length=100, default='новый')

    yearintoservice = models.IntegerField('Год ввода в эксплуатацию', default=0, blank=True, null=True)    
    status = models.CharField(max_length=300, choices=CHOICES, default='В эксплуатации', null=True,
                              verbose_name='Статус: указать "Э" - эксплуатация, "РЕ" - ремонт, "Р" - резерв, "Д" - другое')
    serviceneed = models.BooleanField('Включать в график ТО при автоформировании графика на год (да - "1", нет - "0")', default=True, blank=True, )
    
    individuality = models.TextField('Индивидуальные особенности прибора',  blank=True, null=True)
    notemaster = models.TextField('Примечание (или временное предостережение для сотрудников)',  blank=True, null=True)
    notemetrology = models.TextField('Примечание о метрологическом обеспечении прибора',  blank=True, null=True)
        
    pasport = models.CharField('Ссылка на паспорт', max_length=1000,  blank=True, null=True)
    instruction = models.CharField('Инструкция по эксплуатации (ссылка)', max_length=1000,  blank=True, null=True)
    repair = models.CharField('Контакты для ремонта', max_length=1000,  blank=True, null=True)
        
    price = models.DecimalField('Стоимость (укажите "0" если стоимость неизвестна)', max_digits=100, decimal_places=2, null=True, blank=True, default='0')    
    invnumber = models.CharField('Инвентарный номер (присваивает бухгалтерия)', max_length=100, default='', blank=True, null=True)
    pravo = models.CharField('Право владения прибором (например, номер и дата накладной)', max_length=1000,  blank=True, null=True)
    pravo_have = models.CharField(max_length=300, choices=HAVE, default='cобственность', null=True,
                              verbose_name='Указать "cобственность" или "аренда"')
  
    newperson = models.CharField(verbose_name='Ответственный за оборудование (краткое ФИО сотрудника, например: "И.И.Иванов")', max_length=90, blank=True, null=True)
    newpersondate =  models.CharField('Дата изменения ответственного', blank=True, null=True, max_length=90 )
        
    newroomnumber = models.CharField('Номер комнаты', max_length=100, blank=True, null=True,)
    newroomnumberdate = models.CharField('Дата перемещения', blank=True, null=True, max_length=90)
        
    standard_number = models.CharField('номер в качестве эталона в ФИФ, разряд по ГПС, ЛПС, и т. п.',  default='', blank=True, null=True, max_length=90)

    kategory = models.CharField(max_length=300, choices=KATEGORY, default='Средство измерения', null=True,
                                verbose_name='Категория: указать "СИ", "ИО" или "ВО"')


    def __str__(self):
        try:
            return f'{self.pointer}: {self.exnumber} - зав№ {self.lot}, pk={self.pk}'
        except:
            return f''
                

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid

        super(Equipment, self).save(*args, **kwargs)
        try:
            ServiceEquipmentU.objects.filter(equipment=self).filter(year=str(self.yearintoservice))
        except:
            ServiceEquipmentU.objects.get_or_create(equipment=self, year=str(self.yearintoservice))
    
    class Meta:
        unique_together = ('pointer', 'lot', 'manufacturer', 'yearmanuf')
        verbose_name = 'ЛО список'
        verbose_name_plural = 'ЛО список'


class MeasurEquipmentCharakters(models.Model):
    """Характеристики средств измерений (госреестры в связке с модификациями/типами/диапазонами)"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatormec', editable=True)
    updated_by = CurrentUserField(related_name='updatormec', editable=True)
    name = models.CharField('Название прибора', max_length=10000, default='')
    reestr = models.CharField('Номер в Госреестре', max_length=10000, default='', blank=True, null=True)
    calinterval = models.IntegerField('МежМетрологический интервал, месяцев', default=12, blank=True, null=True)
    typename = models.CharField('Тип/модификация', max_length=1000, default='', blank=True, null=True)
    measurydiapason = models.CharField('Диапазон измерений', max_length=1000, default='', blank=True, null=True)
    accuracity = models.CharField('Класс точности /(разряд/), погрешность и /(или/) неопределённость /(класс, разряд/)',
                                  max_length=1000, default='', blank=True, null=True)
    power = models.BooleanField('Работает от сети (да - "1", нет - "0")', default=False, blank=True)
    voltage = models.CharField('напряжение', max_length=100, default='', blank=True, null=True)
    frequency = models.CharField('частота', max_length=100, default='', blank=True, null=True)
    temperature = models.CharField('температура', max_length=100, default='', blank=True, null=True)
    humidicity = models.CharField('влажность', max_length=100, default='', blank=True, null=True)
    pressure = models.CharField('давление', max_length=100, default='', blank=True, null=True)
    setplace = models.CharField('описание мероприятий по установке', max_length=1000, default='', blank=True, null=True)
    needsetplace = models.BooleanField('Требуется установка (да - "1", нет - "0")', default=False, blank=True)
    complectlist = models.CharField('Где указана комплектация оборудования', max_length=100, default='', blank=True, null=True)
    expresstest = models.BooleanField('Возможно тестирование  (да - "1", нет - "0")', default=False, blank=True)
    traceability = models.TextField('Информация о прослеживаемости (к какому эталону прослеживаются измерения на СИ)',
                                    default='', blank=True, null=True)
    aim = models.CharField('примечание', max_length=90, blank=True, null=True)
    cod = models.CharField('виды измерений, тип (группа) средств измерений по МИ 2314' , max_length=200, blank=True, null=True)
    pointer =  models.CharField('ID добавившей организации', max_length=500, blank=True, null=True) 
                           
    def __str__(self):
        return f'госреестр: {self.reestr},  {self.name} {self.typename}'

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super(MeasurEquipmentCharakters, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'СИ характеристики'
        verbose_name_plural = 'СИ характеристики'
        unique_together = ('reestr', 'typename', 'name', 'pointer')
        
        

class TestingEquipmentCharakters(models.Model):
    """Характеристики ИО"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatortec', editable=True)
    updated_by = CurrentUserField(related_name='updatortec', editable=True)
    name = models.CharField('Название прибора', max_length=10000, default='')
    calinterval = models.IntegerField('МежМетрологический интервал, месяцев', default=12, blank=True, null=True)
    typename = models.CharField('Тип/модификация', max_length=10000, default='', blank=True, null=True)
        
    main_technical_characteristics = models.CharField('Основные технические характеристики', max_length=1000,  blank=True, null=True)
        
    ndoc = models.CharField('Методики испытаний', max_length=500, blank=True, null=True)
        
    power = models.BooleanField('Работает от сети (да - "1", нет - "0")', default=False, blank=True)
    voltage = models.CharField('напряжение', max_length=100, default='', blank=True, null=True)
    frequency = models.CharField('частота', max_length=100, default='', blank=True, null=True)
    temperature = models.CharField('температура', max_length=100, default='', blank=True, null=True)
    humidicity = models.CharField('влажность', max_length=100, default='', blank=True, null=True)
    pressure = models.CharField('давление', max_length=100, default='', blank=True, null=True)
    setplace = models.CharField('описание мероприятий по установке', max_length=1000, default='', blank=True, null=True)
    needsetplace = models.BooleanField('Требуется установка (да - "1", нет - "0")', default=False, blank=True)
    complectlist = models.CharField('Где указана комплектация оборудования', max_length=100, default='', blank=True, null=True)
    expresstest = models.BooleanField('Возможно тестирование  (да - "1", нет - "0")', default=False, blank=True)
    aim = models.CharField('примечание', max_length=90, blank=True, null=True)
    pointer =  models.CharField('ID добавившей организации', max_length=500, blank=True, null=True) 

    def __str__(self):
        return f'{self.name}  {self.typename}'

    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super(TestingEquipmentCharakters, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'ИО характеристики'
        verbose_name_plural = 'ИО характеристики'
        unique_together = ('typename', 'name', 'pointer')



class HelpingEquipmentCharakters(models.Model):
    """Характеристики ВО"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorhec', editable=True)
    updated_by = CurrentUserField(related_name='updatorhec', editable=True)
    name = models.CharField('Название прибора', max_length=1000, default='')
    typename = models.CharField('Тип/модификация', max_length=1000, default='', blank=True, null=True)
    measurydiapason = models.CharField('Основные технические характеристики', max_length=1000,  blank=True, null=True)
    ndoc = models.CharField('Методики испытаний', max_length=500, blank=True, null=True)
    power = models.BooleanField('Работает от сети (да - "1", нет - "0")', default=False, blank=True)
    voltage = models.CharField('напряжение', max_length=100, default='', blank=True, null=True)
    frequency = models.CharField('частота', max_length=100, default='', blank=True, null=True)
    temperature = models.CharField('температура', max_length=100, default='', blank=True, null=True)
    humidicity = models.CharField('влажность', max_length=100, default='', blank=True, null=True)
    pressure = models.CharField('давление', max_length=100, default='', blank=True, null=True)
    setplace = models.CharField('описание мероприятий по установке', max_length=1000, default='', blank=True, null=True)
    needsetplace = models.BooleanField('Требуется установка (да - "1", нет - "0")', default=False, blank=True)
    complectlist = models.CharField('Где указана комплектация оборудования', max_length=100, default='', blank=True, null=True)
    expresstest = models.BooleanField('Возможно тестирование  (да - "1", нет - "0")', default=False, blank=True)
    note = models.CharField('примечание', max_length=90, blank=True, null=True)
    pointer =  models.CharField('ID добавившей организации', max_length=500, blank=True, null=True) 

    def __str__(self):
        return f'{self.name}  {self.typename}'

    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super(HelpingEquipmentCharakters, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'ВО характеристики'
        verbose_name_plural = 'ВО характеристики'
        unique_together = ('typename', 'name', 'pointer')



class MeasurEquipment(models.Model):
    """СИ: составлено из ЛО и характеристик СИ"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorme', editable=True)
    updated_by = CurrentUserField(related_name='updatorme', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True) 
    charakters = models.ForeignKey(MeasurEquipmentCharakters,  on_delete=models.PROTECT,
                                   verbose_name='Характеристики СИ', blank=True, null=True)
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Оборудование')
    aim = models.CharField('Наименование определяемых (измеряемых) характеристик (параметров) продукции',
                           max_length=90, blank=True, null=True)
                                    
    newdate = models.CharField('Дата последней поверки', blank=True, null=True, max_length=90)
    newdatedead = models.CharField('Дата окончания последней поверки', blank=True, null=True, max_length=90)
    newdatedead_date = models.DateField('Дата окончания поверки в формате даты', blank=True, null=True)
    newdateorder = models.CharField('Дата заказа следующей поверки', blank=True, null=True, max_length=90, default='-')
    newdateorder_date = models.DateField('Дата заказа следующей поверки в формате даты', blank=True, null=True)
    newarshin = models.TextField('Ссылка на сведения о поверке в Аршин', blank=True, null=True)
    newcertnumber = models.CharField('Номер последнего свидетельства о поверке', max_length=90, blank=True, null=True)
    newprice = models.DecimalField('Стоимость данной поверки', max_digits=100, decimal_places=2, null=True, blank=True)
    newstatusver = models.CharField(max_length=300, default='Поверен', null=True,
                                 verbose_name='Статус')
    newverificator = models.CharField(verbose_name='Поверитель поверка', blank=True, null=True, max_length=200)
    newplace = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место поверки')
    newnote = models.CharField('Примечание', max_length=900, blank=True, null=True)
    newyear = models.CharField('Год поверки (если нет точных дат)', max_length=900, blank=True, null=True)
    newdateordernew = models.CharField('Дата заказа нового оборудования (если поверять не выгодно)', max_length=90, default='-') 
    newdateordernew_date = models.DateField('Дата заказа нового оборудования в формате даты', blank=True, null=True)
    newhaveorder = models.BooleanField(verbose_name='Заказана следующая поверка (или новое СИ)', default=False,  blank=True)                                 
    newcust = models.BooleanField(verbose_name='Поверку организует Поставщик', default=False, blank=True)                            
    newextra = models.TextField('Дополнительная информация', blank=True, null=True)

    calnewdate = models.CharField('Дата калибровки', blank=True, null=True, max_length=90)
    calnewdatedead = models.CharField('Дата окончания калибровки', blank=True, null=True, max_length=90)
    calnewdateorder = models.CharField('Дата заказа следующей калибровки', blank=True, null=True, max_length=90, default='-')
    calnewarshin = models.TextField('Ссылка на скан сертификата', blank=True, null=True)
    calnewcertnumber = models.CharField('Номер сертификата калибровки', max_length=90, blank=True, null=True)
    calnewprice = models.DecimalField('Стоимость данной калибровки', max_digits=100, decimal_places=2, null=True, blank=True)
    calnewstatusver = models.CharField(max_length=300,  default='Калиброван', null=True,
                                 verbose_name='Статус')
    calnewverificator = models.CharField(verbose_name='Поверитель калибровка', blank=True, null=True, max_length=200)
    calnewplace = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место калибровки')
    calnewnote = models.CharField('Примечание', max_length=900, blank=True, null=True)
    calnewyear = models.CharField('Год калибровки (если нет точных дат)', max_length=900, blank=True, null=True)
    calnewdateordernew = models.CharField('Дата заказа нового оборудования (если калибровать не выгодно)', max_length=90, default='-')
    calnewhaveorder = models.BooleanField(verbose_name='Заказана следующая калибровка (или новое СИ)', default=False, blank=True)                                   
    calnewcust = models.BooleanField(verbose_name='Калибровку организует Поставщик', default=False,
                               blank=True)
    calnewextra = models.TextField('Дополнительная информация', blank=True, null=True)

    def __str__(self):
        try:
            return f'Вн № {self.equipment.exnumber[:5]}  {self.charakters.name}  Зав № {self.equipment.lot} ' \
            f' № реестр {self.charakters.reestr} - pk {self.pk}'
        except:
            return ''

    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super(MeasurEquipment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'СИ список'
        verbose_name_plural = 'СИ список'
        unique_together = ('charakters', 'equipment')
        ordering = ['charakters__name']


class TestingEquipment(models.Model):
    """ИО: составлено из ЛО и характеристик ИО"""
    aim = models.CharField('Наименование видов испытаний и/или определяемых характеристик (параметров) продукции',
                           max_length=500, blank=True, null=True)
    analited_objects = models.CharField('Наименование испытуемых групп объектов',
                            max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorte', editable=True)
    updated_by = CurrentUserField(related_name='updatorte', editable=True)
    charakters = models.ForeignKey(TestingEquipmentCharakters,  on_delete=models.PROTECT,
                                   verbose_name='Характеристики ИО', blank=True, null=True)
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Оборудование')
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)  
        
    newdate = models.CharField('Дата последней аттестации', blank=True, null=True, max_length=90)
    newdatedead = models.CharField('Дата окончания последней аттестации', blank=True, null=True, max_length=90)
    newdatedead_date = models.DateField('Дата окончания аттестации в формате даты', blank=True, null=True)
    newdateorder = models.CharField('Дата заказа следующей аттестации', blank=True, null=True, max_length=90, default='-')
    newdateorder_date = models.DateField('Дата заказа следующей аттестации в формате даты', blank=True, null=True)
    newarshin = models.TextField('Ссылка на скан аттестата', blank=True, null=True)
    newcertnumber = models.CharField('Номер последнего аттестата', max_length=90, blank=True, null=True)
    newprice = models.DecimalField('Стоимость данной аттестации', max_digits=100, decimal_places=2, null=True, blank=True)
    newstatusver = models.CharField(max_length=300, default='Поверен', null=True,
                                 verbose_name='Статус')
    newverificator = models.CharField(verbose_name='Поверитель аттестации', blank=True, null=True, max_length=200)
    newplace = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место аттестации')
    newnote = models.CharField('Примечание', max_length=900, blank=True, null=True)
    newyear = models.CharField('Год аттестации (если нет точных дат)', max_length=900, blank=True, null=True)
    newdateordernew = models.CharField('Дата заказа нового оборудования (если аттестация не выгодна)', max_length=90, default='-')  
    newdateordernew_date = models.DateField('Дата заказа нового оборудования в формате даты', blank=True, null=True)
    newhaveorder = models.BooleanField(verbose_name='Заказана следующая аттестация (или новое ИО)', default=False,  blank=True)                                 
    newcust = models.BooleanField(verbose_name='Аттестацию организует Поставщик', default=False, blank=True)                            
    newextra = models.TextField('Дополнительная информация', blank=True, null=True)


    def __str__(self):
        return f'Вн № {self.equipment.exnumber[:5]}  {self.charakters.name}  Зав № {self.equipment.lot} ' \
               f' - pk {self.pk}'

    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super(TestingEquipment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'ИО список'
        verbose_name_plural = 'ИО список'
        unique_together = ('charakters', 'equipment')
        ordering = ['charakters__name']


class HelpingEquipment(models.Model):
    """ВО: составлено из ЛО и характеристик ВО"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorhe', editable=True)
    updated_by = CurrentUserField(related_name='updatorhe', editable=True)
    charakters = models.ForeignKey(HelpingEquipmentCharakters,  on_delete=models.PROTECT,
                                   verbose_name='Характеристики ВО', blank=True, null=True)
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, verbose_name='Оборудование', blank=True, null=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)  
    aim = models.CharField('Назначение',  max_length=500, blank=True, null=True)
                          

    def __str__(self):
        return f'Вн № {self.equipment.exnumber[:5]}  {self.charakters.name}  Зав № {self.equipment.lot}   - pk {self.pk}'
               

    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super(HelpingEquipment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'ВО список'
        verbose_name_plural = 'ВО список'
        unique_together = ('charakters', 'equipment')
        ordering = ['charakters__name']


# блок 4 - смена комнаты, ответственного, добавление принадлежностей к оборудованию
class Rooms(models.Model):
    """Комнаты лаборатории/производства"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorrr1', editable=True)
    updated_by = CurrentUserField(related_name='updatorrr2', editable=True)
    roomnumber = models.CharField('Номер комнаты', max_length=100, default='')
    person = models.ForeignKey(User, verbose_name='Ответственный за комнату', on_delete=models.PROTECT, blank=True, null=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True) 
    equipment1 = models.ForeignKey(MeasurEquipment, verbose_name='Барометр', null=True,
                                   on_delete=models.PROTECT, blank=True, related_name='equipment1rooms')
    equipment2 = models.ForeignKey(MeasurEquipment, verbose_name='Гигрометр', null=True, related_name='equipment2rooms',
                                   on_delete=models.PROTECT, blank=True)
        

    def __str__(self):
        return self.roomnumber

    def save(self, *args, **kwargs):
            if not self.pointer:
                    self.pointer = self.created_by.profile.userid
            super(Rooms, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('roomnumber', 'pointer',)
        verbose_name = 'Принадлежность: список комнат'
        verbose_name_plural = 'Принадлежность: список комнат'
            

class Personchange(models.Model):
    person = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ответственный за оборудование')
    date = models.DateField('Дата изменения ответственного', auto_now_add=True, db_index=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        try:
            return f'{self.equipment.exnumber} Изменён ответственный {self.date}'
        except:
            return '&'             

    def save(self, *args, **kwargs):
        super().save()
        # добавляем последнего ответственого к СИ
        try:
            note = Equipment.objects.get(pk=self.equipment.pk)
        except:
            pass
        if note:
            note.newperson = self.person.profile.short_name
            newpersondate = get_dateformat(self.date)
            note.newpersondate = newpersondate        
            note.save()

    class Meta:
        verbose_name = 'Принадлежность: изменение ответственного'
        verbose_name_plural = 'Принадлежность: изменение ответственного'


class Roomschange(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True)
    created_by = CurrentUserField(related_name='creatorrc', editable=True)
    updated_by = CurrentUserField(related_name='updatorrc', editable=True)
    roomnumber = models.ForeignKey(Rooms, on_delete=models.PROTECT, verbose_name='Номер комнаты в которой расположено ЛО')
    date = models.DateField('Дата перемещения', auto_now_add=True, db_index=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Оборудование')

    def __str__(self):
        return f'{self.equipment} Перемещено {self.date} '

    def save(self, *args, **kwargs):
        super().save()
            # добавляем последнего ответственого к СИ
        try:
            note = Equipment.objects.get(pk=self.equipment.pk)
            note.newroomnumber = self.roomnumber.roomnumber
            newroomnumberdate = get_dateformat(self.date)
            note.newroomnumberdate = newroomnumberdate  
            note.save()
        except:
            pass

    class Meta:
        verbose_name = 'Принадлежность: изменение комнаты'
        verbose_name_plural = 'Принадлежность: изменение комнаты'


class DocsCons(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatordoc', editable=True)
    updated_by = CurrentUserField(related_name='updatordoc', editable=True)
    date = models.CharField('Дата появления',  max_length=1000, default='', blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, blank=True, null=True,
                                  verbose_name='Оборудование')
    docs = models.CharField('Документ или принадлежность (1 или несколько)', max_length=100, default='', blank=True,
                            null=True)
    source = models.CharField('Откуда появился', max_length=1000, default='От поставщика', blank=True, null=True)
    note = models.CharField('Примечание', max_length=1000, blank=True, null=True)

    def __str__(self):
        return f'{self.equipment.exnumber} '

    class Meta:
        verbose_name = 'ЛО комплект к прибору'
        verbose_name_plural = 'ЛО комплекты к приборам'


# блок 5 - проверка СИ, аттестация ИО, проверка характеристик ВО


class Verificationequipment(models.Model):
    """Поверка СИ"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorvme', editable=True)
    updated_by = CurrentUserField(related_name='updatorvme', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    equipmentSM = models.ForeignKey(MeasurEquipment, verbose_name='СИ',
                                    on_delete=models.PROTECT, related_name='equipmentSM_ver', blank=True, null=True)
    date = models.DateField('Дата поверки', blank=True, null=True)
    datedead = models.DateField('Дата окончания поверки', blank=True, null=True)
    dateorder = models.DateField('Дата заказа следующей поверки', blank=True, null=True)
    arshin = models.CharField('Ссылка на сведения о поверке в Аршин', blank=True, null=True, max_length=1000)
    certnumber = models.CharField('Номер свидетельства о поверке', max_length=90, blank=True, null=True)
    price = models.DecimalField('Стоимость данной поверки', max_digits=100, decimal_places=2, null=True, blank=True)
    img = models.ImageField('Сертификат', upload_to='user_images', blank=True, null=True)
    statusver = models.CharField(max_length=300, choices=CHOICESVERIFIC, default='Поверен', null=True,
                                 verbose_name='Статус поверки: выберите "Поверен", "Признан непригодным", "Спорный"')
    verificator = models.ForeignKey(Verificators, on_delete=models.PROTECT,
                                    verbose_name='Название компании поверителя', blank=True, null=True)
    place = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место поверки: выберите "У поверителя", "На месте эксплуатации"')
    note = models.CharField('Примечание', max_length=900, blank=True, null=True)
    year = models.CharField('Год поверки (если нет точных дат)', max_length=900, blank=True, null=True)
    dateordernew = models.DateField('Дата заказа нового оборудования (если поверять не выгодно)',
                                    blank=True, null=True)
    haveorder = models.BooleanField(verbose_name='Заказана следующая поверка (или новое СИ): "1" - заказана, "0" - не заказана', default=False,
                                    blank=True)
    cust = models.BooleanField(verbose_name='Поверку организует Поставщик: "1" - да, "0" - нет', default=False,
                               blank=True)
    extra = models.TextField('Выписка из сведений о поверке', blank=True, null=True)

    def __str__(self):
        try:
            return f'Поверка  вн № ' \
               f'  {self.equipmentSM.equipment.exnumber} {self.equipmentSM.charakters.name} от {self.date} ' \
                   f'до {self.datedead} {self.year}'
        except:
            return '&'

    def get_absolute_url(self):
        """ Создание юрл объекта для перенаправления из вьюшки создания объекта на страничку с созданным объектом """
        return reverse('measureequipmentver', kwargs={'str': self.equipmentSM.equipment.exnumber})
            
    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super().save()
        # добавляем последнюю поверку к оборудованию
        try:
            note = MeasurEquipment.objects.get(pk=self.equipmentSM.pk)
        except:
            pass
        if note:       
            note.newcertnumber = self.certnumber
            note.newarshin = self.arshin
            note.newprice = self.price
            note.newstatusver = self.statusver
            note.newverificator = self.verificator.companyName
            note.newplace = self.place
            note.newnote = self.note
            note.newyear = self.year
            note.newhaveorder = self.haveorder
            note.newcust = self.cust
            note.newextra = self.extra 
            newdatedead = get_dateformat(self.datedead)
            note.newdatedead = newdatedead 
            note.newdatedead_date = self.datedead
            newdate = get_dateformat(self.date)
            note.newdate = newdate
            note.newdate_date = self.date
            if self.dateorder:
                newdateorder = get_dateformat(self.dateorder)
                note.newdateorder = newdateorder
                note.newdateorder_date = self.dateorder
            else:
                note.newdateorder = '-' 
            if self.dateordernew:
                newdateordernew = get_dateformat(self.dateordernew)
                note.newdateordernew = newdateordernew  
                note.newdateordernew_date = self.dateordernew
            else:
                note.newdateordernew = '-' 
            note.save()

    class Meta:
        verbose_name = 'СИ метрология поверка'
        verbose_name_plural = 'СИ метрология поверка'


class Calibrationequipment(models.Model):
    """Калибровка СИ"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorcme', editable=True)
    updated_by = CurrentUserField(related_name='updatorcme', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    equipmentSM = models.ForeignKey(MeasurEquipment, verbose_name='СИ',
                                    on_delete=models.PROTECT, related_name='equipmentSM_cal', blank=True, null=True)
    date = models.DateField('Дата калибровки', blank=True, null=True)
    datedead = models.DateField('Дата окончания калибровки', blank=True, null=True)
    dateorder = models.DateField('Дата заказа следующей калибровки', blank=True, null=True)
    arshin = models.TextField('Ссылка на скан сертификата', blank=True, null=True, max_length=1000)
    certnumber = models.CharField('Номер сертификата калибровки', max_length=90, blank=True, null=True)
    price = models.DecimalField('Стоимость данной калибровки', max_digits=100, decimal_places=2, null=True, blank=True)
    statusver = models.CharField(max_length=300, choices=CHOICESCAL, default='Калиброван', null=True,
                                 verbose_name='Статус калибровки: выберите "Калиброван", "Признан непригодным", "Спорный"')
    verificator = models.ForeignKey(Verificators, on_delete=models.PROTECT,
                                    verbose_name='Название компании поверителя', blank=True, null=True)
    place = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место калибровки: выберите "У поверителя", "На месте эксплуатации"')
    note = models.CharField('Примечание', max_length=900, blank=True, null=True)
    year = models.CharField('Год калибровки (если нет точных дат)', max_length=900, blank=True, null=True)
    dateordernew = models.DateField('Дата заказа нового оборудования (если калибровать не выгодно)',
                                    blank=True, null=True)
    haveorder = models.BooleanField(verbose_name='Заказана следующая калибровки (или новое СИ): "1" - заказана, "0" - не заказана', default=False,
                                    blank=True)
    cust = models.BooleanField(verbose_name='Калибровку организует Поставщик: "1" - да, "0" - нет', default=False,
                               blank=True)
    extra = models.TextField('Выписка из сертификата калибровки', blank=True, null=True)

    def __str__(self):
        try:
            return f'Калибровка  вн № ' \
               f'  {self.equipmentSM.equipment.exnumber} {self.equipmentSM.charakters.name} от {self.date} ' \
                   f'до {self.datedead} {self.year}'
        except:
            return '&'

    def get_absolute_url(self):
        """ Создание юрл объекта для перенаправления из вьюшки создания объекта на страничку с созданным объектом """
        return reverse('measureequipmentcal', kwargs={'str': self.equipmentSM.equipment.exnumber})


    def save(self, *args, **kwargs):
        if not self.pointer:
            self.pointer = self.created_by.profile.userid
        super().save()
        # добавляем последнюю калибровку к оборудованию
        try:
            note = MeasurEquipment.objects.get(pk=self.equipmentSM.pk)
        except:
            pass
        if note:
            note = MeasurEquipment.objects.get(pk=self.equipmentSM.pk)
            note.calnewcertnumber = self.certnumber
            note.calnewarshin = self.arshin
            note.calnewprice = self.price
            note.calnewstatusver = self.statusver
            note.calnewverificator = self.verificator.companyName
            note.calnewplace = self.place
            note.calnewnote = self.note
            note.calnewyear = self.year
            note.calnewhaveorder = self.haveorder
            note.calnewcust = self.cust
            note.calnewextra = self.extra      
            calnewdate = get_dateformat(self.date)
            note.calnewdate = calnewdate
            calnewdatedead = get_dateformat(self.datedead)
            note.calnewdatedead = calnewdatedead
            if self.dateorder:
                calnewdateorder = get_dateformat(self.dateorder)
                note.calnewdateorder = calnewdateorder
            else:
                note.calnewdateorder = '-' 
            if self.dateordernew:
                calnewdateordernew = get_dateformat(self.dateordernew)
                note.calnewdateordernew = calnewdateordernew  
            else:
                note.calnewdateordernew = '-'            
            note.save()

    class Meta:
        verbose_name = 'СИ метрология калибровка'
        verbose_name_plural = 'СИ метрология калибровка'


class Attestationequipment(models.Model):
    """Аттестация ИО"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorate', editable=True)
    updated_by = CurrentUserField(related_name='updatorate', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    arshin = models.TextField('Ссылка на скан аттестата', blank=True, null=True, max_length=1000)
    equipmentSM = models.ForeignKey(TestingEquipment, verbose_name='ИО',
                                    on_delete=models.PROTECT, related_name='equipmentSM_att', blank=True, null=True)
    date = models.DateField('Дата аттестации', blank=True, null=True)
    datedead = models.DateField('Дата окончания аттестации', blank=True, null=True)
    dateorder = models.DateField('Дата заказа следующей аттестации', blank=True, null=True)
    certnumber = models.CharField('Номер аттестата', max_length=90, blank=True, null=True)
    price = models.DecimalField('Стоимость данной аттестации', max_digits=100, decimal_places=2, null=True, blank=True)
    img = models.ImageField('Аттестат', upload_to='user_images', blank=True, null=True)
    statusver = models.CharField(max_length=300, choices=CHOICESATT, default='Аттестован', null=True,
                                 verbose_name='Статус аттестации: выберите "Аттестован", "Признан непригодным", "Спорный"')
    verificator = models.ForeignKey(Verificators, on_delete=models.PROTECT,
                                    verbose_name='Название компании поверителя', blank=True, null=True)
    place = models.CharField(max_length=300, choices=CHOICESPLACE, default='У поверителя', null=True,
                             verbose_name='Место аттестации: выберите "У поверителя", "На месте эксплуатации"')
    note = models.CharField('Примечание', max_length=900, blank=True, null=True)
    year = models.CharField('Год аттестации (если нет точных дат)', max_length=900, blank=True, null=True)
    dateordernew = models.DateField('Дата заказа нового оборудования (если аттестовывать не выгодно)',
                                    blank=True, null=True)
    haveorder = models.BooleanField(verbose_name='Заказана следующая аттестация (или новое ИО): "1" - заказана, "0" - не заказана', default=False,
                                    blank=True)
    cust = models.BooleanField(verbose_name='Аттестацию организует Поставщик: "1" - да, "0" - нет', default=False,
                               blank=True)
    extra = models.TextField('Выписка из аттестата', blank=True, null=True)

    def __str__(self):
        try:
            return f'Аттестация  вн № ' \
                   f'  {self.equipmentSM.equipment.exnumber} {self.equipmentSM.charakters.name} от {self.date} до' \
                   f' {self.datedead} {self.year}'
        except:
            return '&'

    def get_absolute_url(self):
        """ Создание юрл объекта для перенаправления из вьюшки создания объекта на страничку с созданным объектом """
        return reverse('testingequipmentatt', kwargs={'str': self.equipmentSM.equipment.exnumber})

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super().save()
        # добавляем последнюю аттестацию к оборудованию
        try:
            note = TestingEquipment.objects.get(pk=self.equipmentSM.pk)
        except:
            pass
        if note:       
            note.newcertnumber = self.certnumber
            note.newarshin = self.arshin
            note.newprice = self.price
            note.newstatusver = self.statusver
            note.newverificator = self.verificator.companyName
            note.newplace = self.place
            note.newnote = self.note
            note.newyear = self.year
            note.newhaveorder = self.haveorder
            note.newcust = self.cust
            note.newextra = self.extra 
            newdatedead = get_dateformat(self.datedead)
            note.newdatedead = newdatedead 
            note.newdatedead_date = self.datedead
            newdate = get_dateformat(self.date)
            note.newdate = newdate
            note.newdate_date = self.date
            if self.dateorder:
                newdateorder = get_dateformat(self.dateorder)
                note.newdateorder = newdateorder
                note.newdateorder_date = self.dateorder
            else:
                note.newdateorder = '-' 
            if self.dateordernew:
                newdateordernew = get_dateformat(self.dateordernew)
                note.newdateordernew = newdateordernew  
                note.newdateordernew_date = self.dateordernew
            else:
                note.newdateordernew = '-' 
            note.save()



    def save(self, *args, **kwargs):
        super().save()
        # добавляем последнюю аттестацию к оборудованию
        try:
            note = TestingEquipment.objects.get(pk=self.equipmentSM.pk)
        except:
            pass
        if note:       
            note.newcertnumber = self.certnumber
            note.newarshin = self.arshin
            note.newprice = self.price
            note.newstatusver = self.statusver
            note.newverificator = self.verificator.companyName
            note.newplace = self.place
            note.newnote = self.note
            note.newyear = self.year
            note.newhaveorder = self.haveorder
            note.newcust = self.cust
            note.newextra = self.extra 
            newdatedead = get_dateformat(self.datedead)
            note.newdatedead = newdatedead 
            note.newdatedead_date = self.datedead
            if self.dateorder:
                newdateorder = get_dateformat(self.dateorder)
                note.newdateorder = newdateorder
                note.newdateorder_date = self.dateorder
            else:
                note.newdateorder = '-' 
            if self.dateordernew:
                newdateordernew = get_dateformat(self.dateordernew)
                note.newdateordernew = newdateordernew  
                note.newdateordernew_date = self.dateordernew
            else:
                note.newdateordernew = '-' 
            note.save()    
    class Meta:
        verbose_name = 'ИО метрология аттестация'
        verbose_name_plural = 'ИО метрология аттестация'



# блок 6 - комментарии

class CommentsEquipment(models.Model):
    """стандартнрый класс для комментариев"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorcomm', editable=True)
    updated_by = CurrentUserField(related_name='updatorcomm', editable=True)
    date = models.DateField('Дата',  db_index=True)
    note = models.TextField('Содержание', max_length=1000, default='')
    forNote = models.ForeignKey(Equipment, verbose_name='К прибору', on_delete=models.CASCADE)
    author = models.CharField('Автор', max_length=90, blank=True, null=True)
    type = models.CharField('Тип записи', max_length=90, blank=True, null=True, choices=NOTETYPE)
    img = models.ImageField('Фото', upload_to='user_images', blank=True, null=True)

    def __str__(self):
        return f' {self.author} , {self.forNote.exnumber},  {self.date}'

    def get_absolute_url(self):
        """ Создание юрл объекта для перенаправления из вьюшки создания объекта на страничку с созданным объектом """
        return reverse('measureequipmentcomm', kwargs={'str': self.forNote.exnumber})

    def save(self, *args, **kwargs):
        self.author = self.created_by.profile.short_name
        super().save()
        
        if self.img:
                image = Image.open(self.img.path)
                if image.height > 1000 or image.width > 1000:
                    resize = (1000, 1000)
                    image.thumbnail(resize)
                    image.save(self.img.path)
                

    class Meta:
        verbose_name = 'ЛО записи в карточках'
        verbose_name_plural = 'ЛО записи в карточках'


class CommentsVerificationequipment(models.Model):
    """комментарии к поверке """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorcommver', editable=True)
    updated_by = CurrentUserField(related_name='updatorcommver', editable=True)
    date = models.DateField('Дата', auto_now_add=True, db_index=True)
    note = models.TextField('Содержание', max_length=1000, default='')
    forNote = models.ForeignKey(Equipment, verbose_name='К прибору', on_delete=models.CASCADE)
    author = models.CharField('Автор', max_length=90, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('measureequipmentver', kwargs={'str': self.forNote.exnumber})

    class Meta:
        verbose_name = 'СИ Комментарий к поверке'
        verbose_name_plural = 'СИ Комментарий к поверке'


class CommentsAttestationequipment(models.Model):
    """комментарии к аттестации """
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True)
    created_by = CurrentUserField(related_name='creatorcommatt', editable=True)
    updated_by = CurrentUserField(related_name='updatorcommatt', editable=True)
    date = models.DateField('Дата', auto_now_add=True, db_index=True)
    note = models.TextField('Содержание', max_length=1000, default='')
    forNote = models.ForeignKey(Equipment, verbose_name='К прибору', on_delete=models.CASCADE)
    author = models.CharField('Автор', max_length=90, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('testingequipmentatt', kwargs={'str': self.forNote.exnumber})

    class Meta:
        verbose_name = 'ИО Комментарий к аттестации'
        verbose_name_plural = 'ИО Комментарий к аттестации'


# блок 7 - микроклимат в помещении

class MeteorologicalParameters(models.Model):
    """микроклимат в помещении"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatormeteo', editable=True)
    updated_by = CurrentUserField(related_name='updatormeteo', editable=True)
    date = models.DateField('Дата')
    roomnumber = models.ForeignKey(Rooms, on_delete=models.PROTECT)
    pressure = models.CharField('Давление, кПа', max_length=90, blank=True, null=True)
    temperature = models.CharField('Температура, °С', max_length=90, blank=True, null=True)
    humidity = models.CharField('Влажность, %', max_length=90, blank=True, null=True)
    equipments = models.CharField('СИ', max_length=190, blank=True, null=True)
    person = models.CharField('Исполнитель ФИО', max_length=190, blank=True, null=True)
    

    def __str__(self):
        return f' {self.date} , {self.roomnumber.roomnumber}'
            
    def save(self, *args, **kwargs):
        self.equipments = f'{self.roomnumber.equipment1.charakters.name} тип {self.roomnumber.equipment1.charakters.typename}, заводской номер {self.roomnumber.equipment1.equipment.lot}, '\
        f'свидетельство о поверке № {self.roomnumber.equipment1.newcertnumber}, действительно до {self.roomnumber.equipment1.newdatedead}; '\
        f'{self.roomnumber.equipment2.charakters.name} тип {self.roomnumber.equipment2.charakters.typename}, заводской номер {self.roomnumber.equipment2.equipment.lot}, '\
        f'свидетельство о поверке № {self.roomnumber.equipment2.newcertnumber}, действительно до {self.roomnumber.equipment2.newdatedead};'
        self.person = self.roomnumber.person.profile.short_name
        return super(MeteorologicalParameters, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Микроклимат: записи'
        verbose_name_plural = 'Микроклимат: записи'
        unique_together = ('date', 'roomnumber',)


# блок 8 - техобслуживание

class ServiceEquipmentME(models.Model):
    """Техобслуживание СИ - постоянная информация из паспортов и инструкций"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorserme', editable=True)
    updated_by = CurrentUserField(related_name='updatorserme', editable=True)
    pointer =  models.CharField('ID организации кто вносил запись', max_length=500, blank=True, null=True) 
    charakters = models.OneToOneField(MeasurEquipmentCharakters,  on_delete=models.PROTECT,
                                   verbose_name='Характеристики СИ')
    # ТО 0
    descriptiont0 = models.TextField('Объем технического обслуживания ТО 0',  default='', blank=True)

    # ТО 1
    descriptiont1 = models.TextField('Объем технического обслуживания ТО 1',  default='', blank=True)

    # ТО 2
    descriptiont2 = models.TextField('Объем технического обслуживания ТО 2',  default='', blank=True)

    comment = models.TextField('Комментарий к постоянным особенностям ТО',  default='', blank=True)

    def __str__(self):
        return f'{self.charakters.name}, pk = {self.pk}'

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super().save()

    class Meta:
        verbose_name = 'ТО СИ постоянная информация'
        verbose_name_plural = 'ТО СИ постоянная информация'


class ServiceEquipmentTE(models.Model):
    """Техобслуживание ИО"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorserte', editable=True)
    updated_by = CurrentUserField(related_name='updatorserte', editable=True)
    pointer =  models.CharField('ID организации кто вносил запись', max_length=500, blank=True, null=True) 
    charakters = models.OneToOneField(TestingEquipmentCharakters, on_delete=models.PROTECT,
                                   verbose_name='Характеристики ИО')

    # ТО 0
    descriptiont0 = models.TextField('Объем технического обслуживания ТО 0',  default='', blank=True)

    # ТО 1
    descriptiont1 = models.TextField('Объем технического обслуживания ТО 1',  default='', blank=True)

    # ТО 2
    descriptiont2 = models.TextField('Объем технического обслуживания ТО 2',  default='', blank=True)

    comment = models.TextField('Комментарий к постоянным особенностям ТО',  default='', blank=True)

    def __str__(self):
        return self.charakters.name

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super().save()

    class Meta:
        verbose_name = 'ТО ИО постоянная информация'
        verbose_name_plural = 'ТО ИО постоянная информация'


class ServiceEquipmentHE(models.Model):
    """Техобслуживание ВО"""
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, editable=True)
    created_by = CurrentUserField(related_name='creatorserhe', editable=True)
    updated_by = CurrentUserField(related_name='updatorserhe', editable=True)
    pointer =  models.CharField('ID организации кто вносил запись', max_length=500, blank=True, null=True) 
    charakters = models.OneToOneField(HelpingEquipmentCharakters, on_delete=models.PROTECT,
                                   verbose_name='Характеристики ВО')
    
    # ТО 0
    descriptiont0 = models.TextField('Объем технического обслуживания ТО 0',  default='', blank=True)

    # ТО 1
    descriptiont1 = models.TextField('Объем технического обслуживания ТО 1',  default='', blank=True)

    # ТО 2
    descriptiont2 = models.TextField('Объем технического обслуживания ТО 2',  default='', blank=True)
        
    comment = models.TextField('Комментарий к постоянным особенностям ТО',  default='', blank=True)


    def __str__(self):
        return self.charakters.name

    def save(self, *args, **kwargs):
        if not self.pointer:
                self.pointer = self.created_by.profile.userid
        super().save()

    class Meta:
        verbose_name = 'ТО ВО постоянная информация'
        verbose_name_plural = 'ТО ВО постоянная информация'


class ServiceEquipmentU(models.Model):
    """Техобслуживание всего лабораторного оборудования индивидуальная информация ПЛАН"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorserp', editable=True)
    updated_by = CurrentUserField(related_name='updatorserp', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    year =  models.CharField('Год ТО-2 план', max_length=4, blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Оборудование')
    commentservice = models.TextField('Примечание к ТОиР', default='', blank=True, null=True)
    # ТО 2
    t2month1 = models.BooleanField('ТО 2 в месяце 1', default=True)
    t2month2 = models.BooleanField('ТО 2 в месяце 2', default=False)
    t2month3 = models.BooleanField('ТО 2 в месяце 3', default=False)
    t2month4 = models.BooleanField('ТО 2 в месяце 4', default=True)
    t2month5 = models.BooleanField('ТО 2 в месяце 5', default=False)
    t2month6 = models.BooleanField('ТО 2 в месяце 6', default=False)
    t2month7 = models.BooleanField('ТО 2 в месяце 7', default=True)
    t2month8 = models.BooleanField('ТО 2 в месяце 8', default=False)
    t2month9 = models.BooleanField('ТО 2 в месяце 9', default=False)
    t2month10 = models.BooleanField('ТО 2 в месяце 10', default=True)
    t2month11 = models.BooleanField('ТО 2 в месяце 11', default=False)
    t2month12 = models.BooleanField('ТО 2 в месяце 12', default=False)

    def __str__(self):
        return f'pk = {self.pk}'
            
    def save(self, *args, **kwargs):
        self.pointer = self.equipment.pointer
        super(ServiceEquipmentU, self).save(*args, **kwargs)
        ServiceEquipmentUFact.objects.get_or_create(equipment=self.equipment, pk_pointer=self.pk, year=self.year)
                    
    class Meta:
        verbose_name = 'ТО ЛО: ТО-2 план'
        verbose_name_plural = 'ТО ЛО: ТО-2 план'




class ServiceEquipmentUFact(models.Model):
    """Техобслуживание всего лабораторного оборудования индивидуальная информация факт"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorserf', editable=True)
    updated_by = CurrentUserField(related_name='updatorserf', editable=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    year =  models.CharField('Год ТО-2 факт', max_length=4, blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Оборудование')
    pk_pointer=models.CharField('указатель на pk соответствующего ТО-2 план', max_length=20, blank=True, null=True)
    # ТО 2
    t2month1 = models.BooleanField('ТО 2 в месяце 1', default=True)
    t2month2 = models.BooleanField('ТО 2 в месяце 2', default=False)
    t2month3 = models.BooleanField('ТО 2 в месяце 3', default=False)
    t2month4 = models.BooleanField('ТО 2 в месяце 4', default=True)
    t2month5 = models.BooleanField('ТО 2 в месяце 5', default=False)
    t2month6 = models.BooleanField('ТО 2 в месяце 6', default=False)
    t2month7 = models.BooleanField('ТО 2 в месяце 7', default=True)
    t2month8 = models.BooleanField('ТО 2 в месяце 8', default=False)
    t2month9 = models.BooleanField('ТО 2 в месяце 9', default=False)
    t2month10 = models.BooleanField('ТО 2 в месяце 10', default=True)
    t2month11 = models.BooleanField('ТО 2 в месяце 11', default=False)
    t2month12 = models.BooleanField('ТО 2 в месяце 12', default=False)

    def __str__(self):
        return f'pk = {self.pk}'
            
    def save(self, *args, **kwargs):
        self.pointer = self.equipment.pointer
        return super(ServiceEquipmentUFact, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'ТО ЛО: ТО-2 факт'
        verbose_name_plural = 'ТО ЛО: ТО-2 факт'



# блок 9 - отправка в поверку
class Agreementverification(models.Model):
    """Договоры организации с поверителями"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatoragr', editable=True)
    updated_by = CurrentUserField(related_name='updatoragr', editable=True)
    verificator = models.ForeignKey(Verificators, on_delete=models.PROTECT, verbose_name='Поверитель')    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')  
    ver_agreement_number = models.CharField('Номер договора с организацией-поверителем', max_length=100, default=None, null=True, blank=True)
    ver_agreement_date = models.CharField('Дата договора с организацией-поверителем', max_length=100, default=None, null=True, blank=True)
    ver_agreement_card = models.CharField('Номер учетной карточки у организации-поверителя', max_length=100, default=None, null=True, blank=True)
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
    active = models.BooleanField('Активный', default=False, blank=True)
    public_agree = models.BooleanField('Согласие на передачу данных в Аршин', default=True, blank=True)

    def save(self, *args, **kwargs):
        super().save()        
        self.pointer = self.company.userid
        try:
            Activeveraqq.objects.get(company=self.company)
        except:
            Activeveraqq.objects.get_or_create(aqq=self, company=self.company)

        
    def __str__(self):
        return self.verificator.companyName
    class Meta:
        verbose_name = 'Контрагенты: Договоры с поверителями'
        verbose_name_plural = 'Контрагенты: Договоры с поверителями'


class Activeveraqq(models.Model):
    """Активный договор с поверителем"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')  
    aqq = models.ForeignKey(Agreementverification, on_delete=models.CASCADE, verbose_name='Договор с поверителем', unique=True, null=True) 
    pointer =  models.CharField('ID организации', max_length=500, blank=True, null=True)
         
    def save(self, *args, **kwargs):
        self.pointer = self.company.userid
            
        return super(Activeveraqq, self).save(*args, **kwargs)
        
    def __str__(self):
        try:
            return self.aqq.verificator.companyName
        except: 
            return ''

            
    class Meta:
        verbose_name = 'Контрагенты: Договор с поверителем активный'
        verbose_name_plural = 'Контрагенты: Договор с поверителем активный'

