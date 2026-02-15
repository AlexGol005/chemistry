from django.db import models  
from django.contrib.auth.models import User
from django_currentuser.db.models import CurrentUserField
from decimal import *
from datetime import timedelta, date
from PIL import  Image

now = date.today()
monthly_payment = Decimal(4000)

REASON_CHOICES = (
        ('Пополнение счёта автоматическое', 'Пополнение счёта автоматическое'),
        ('Пополнение счёта оператором', 'Пополнение счёта оператором'),
        ('Автоматическое списание ежемесячного платежа', 'Автоматическое списание ежемесячного платежа'),
        ('Другое', 'Другое'),
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    name = models.CharField('ФИО', max_length=40, null=True, blank=True)
    short_name = models.CharField('ФИО кратко для документов', max_length=40, null=True, blank=True, default = 1)
    user_email = models.CharField('email', max_length=40, null=True, blank=True, default = 1)
    user_phone = models.CharField('телефон', max_length=40, null=True, blank=True, default = 1)
    userposition = models.CharField('Должность', max_length=50, null=True, blank=True, default = 1)
    userid = models.CharField('Идентификатор организации (20 случайных цифр и латинских букв)', max_length=50, default = "chem", null=True, blank=True)
    main_user = models.BooleanField ('Главный пользователь - галочка если да', default=False)
    img = models.ImageField('Фото сотрудника', default='user_images/default.png', upload_to='user_images')


    def __str__(self):
        return f'Организация: {self.userid}; пользователь: {self.name}; логин: {self.user.username}'

    def save(self, *args, **kwargs):
        super().save()
        image = Image.open(self.img.path)
        if image.height > 256 or image.width > 256:
            resize = (256, 256)
            image.thumbnail(resize)
            image.save(self.img.path)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'



class Company(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorcompany', editable=True)
    updated_by = CurrentUserField(related_name='updatorcompany', editable=True)
    userid = models.CharField('Идентификатор организации (20 случайных цифр и латинских букв)', max_length=50, default=None, null=True, blank=True, unique=True)
    name = models.CharField('Название организации краткое', max_length=100, default=None, null=True, blank=True, unique=True)
    name_big = models.CharField('Название организации полное', max_length=100, default=None, null=True, blank=True, unique=True)
    attestat = models.CharField('Аттестат аккредитации', max_length=500, default=None, null=True, blank=True)
    requisits =  models.TextField('Реквизиты организации', default=None, null=True, blank=True)
    adress =  models.TextField('Адрес организации юридический', max_length=100, default=None, null=True, blank=True)
    adress_lab =  models.TextField('Адрес лаборатории физический', max_length=100, default=None, null=True, blank=True)
    phone =  models.CharField('Телефон организации юридический', max_length=20, default=None, null=True, blank=True)
    phone_lab =  models.CharField('Телефон лаборатории', max_length=20, default=None, null=True, blank=True)
    direktor_position = models.CharField('Должность главного лица компании', max_length=40, default=None, null=True, blank=True)
    direktor_name = models.CharField('ФИО главного лица компании', max_length=100, default=None, null=True, blank=True)
    headlab_position = models.CharField('Должность главного лица лаборатории', max_length=100, default=None, null=True, blank=True)
    headlab_name = models.CharField('ФИО главного лица лаборатории', max_length=100, default=None, null=True, blank=True)
    manager_position = models.CharField('Должность лица ответственного за оборудование', max_length=100, default=None, null=True, blank=True)
    manager_name = models.CharField('ФИО лица ответственного за оборудование', max_length=100, default=None, null=True, blank=True)
    manager_email = models.CharField('email лица ответственного за оборудование', max_length=100, default=None, null=True, blank=True)
    manager_phone = models.CharField('телефон лица ответственного за оборудование', max_length=100, default=None, null=True, blank=True)
    caretaker_position = models.CharField('Должность завхоза', max_length=100, default=None, null=True, blank=True)
    caretaker_name = models.CharField('ФИО завхоза', max_length=100, default=None, null=True, blank=True)
    email = models.CharField('email организации', max_length=40, default=None, null=True, blank=True)
    pay = models.BooleanField ('Оплачено', default=True)
    balance = models.DecimalField('Балланс счёта', max_digits=18, decimal_places=2, default=0)
    payement_date = models.DateField('Дата платежа', default=None, null=True, blank=True)   

    def __str__(self):
        if self.created_at:
            return f'Организация: {self.userid}; {self.name} - от {self.created_at}'
        else:
            return f'Организация: {self.userid}; {self.name}'

    def save(self, *args, **kwargs):
        if not self.payement_date:
            self.payement_date = now + timedelta(days=30)
        super(Company, self).save(*args, **kwargs)  
            
                    
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


class Employees(models.Model):
    userid = models.ForeignKey(Company, verbose_name = 'Идентификатор организации', on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField('ФИО', max_length=40, default=None, null=True, blank=True)
    position = models.CharField('Должность', max_length=40, default=None, null=True, blank=True)


    def __str__(self):
        return f'{self.name};{self.position};({self.userid.userid}) '

    class Meta:
        verbose_name = 'Сотрудники'
        verbose_name_plural = 'Сотрудники'


class CompanyBalanceChange(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorbalancechange', editable=True)
    updated_by = CurrentUserField(related_name='updatorbalancechange', editable=True)
    company = models.ForeignKey('Company', verbose_name ='Компания', on_delete=models.PROTECT)
    reason = models.CharField(choices=REASON_CHOICES, verbose_name ='Источник изменения', max_length=100, default=None, null=True, blank=True)
    document = models.CharField(verbose_name ='Номер документа', max_length=100, default=None, null=True, blank=True)
    amount = models.DecimalField('Сумма', default=0, max_digits=18, decimal_places=2)
    
    def save(self, *args, **kwargs): 
        # меняем балланс компании
        if not self.pk:
            note = self.company
            note.balance = note.balance + self.amount
            note.save() 
        super(CompanyBalanceChange, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.company.name};{self.amount};({self.created_at}) '

    class Meta:
        verbose_name = 'Изменения балланса компании'
        verbose_name_plural = 'Изменения балланса компании'


class CompanyActiveEmployesLists(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    created_by = CurrentUserField(related_name='creatorael', editable=True)
    updated_by = CurrentUserField(related_name='updatorael', editable=True)
    company = models.ForeignKey('Company', verbose_name ='Компания', on_delete=models.PROTECT)
    list_employees = models.CharField(verbose_name ='Список pk активных сотрудников', max_length=100, default=None, null=True, blank=True)


    def __str__(self):
        return f'{self.company.name};{self.list_employees}) '

    class Meta:
        verbose_name = 'Список активных сотрудников компании'
        verbose_name_plural = 'Список активных сотрудников компании'



