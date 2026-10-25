from datetime import timedelta, date, datetime
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from users.models import *

now = date.today()
nowtime = datetime.today().isoformat()

# Функция отправки сообщения
def email(subject, content, user_email):
    send_mail(
        subject,
        content,
        'sandra.005@mail.ru',
        [user_email, 'sandra.005@mail.ru']
    )

class Command(BaseCommand):
    def take_rent(self):
        # ВНИМАНИЕ: Укажите здесь вашу стоимость ежемесячного платежа цифрой.
        # Либо, если у компании есть динамическое поле, замените ниже monthly_payment на i.monthly_payment
        monthly_payment = 1000  

        note_list = Company.objects.filter(payement_date=now)
        not_pay_i = []
        pay_i = []
        for i in note_list:
            if i.balance >= monthly_payment:
                CompanyBalanceChange.objects.create(
                    company=i, 
                    reason='Автоматическое списание ежемесячного платежа', 
                    amount=-monthly_payment
                )
                i.payement_date = i.payement_date + timedelta(days=30)
                i.pay = True
                pay_i.append(i)
                i.save()
                main_user = Profile.objects.filter(userid=i.userid).get(main_user=True)
                g_add = Group.objects.get(name='Продвинутый пользователь')
                g_rem = Group.objects.get(name='Базовый пользователь')
                c_main_user = main_user.user
                g_add.user_set.add(c_main_user) 
                g_rem.user_set.remove(c_main_user)
            else:
                i.payement_date = i.payement_date + timedelta(days=1)
                i.pay = False
                not_pay_i.append(i)
                i.save() 
                main_user = Profile.objects.filter(userid=i.userid).get(main_user=True)
                g_add = Group.objects.get(name='Базовый пользователь')
                g_rem = Group.objects.get(name='Продвинутый пользователь')
                c_main_user = main_user.user
                g_add.user_set.add(c_main_user) 
                g_rem.user_set.remove(c_main_user)
                
        not_pay_companies = CompanyActiveEmployesLists.objects.filter(company__in=not_pay_i)
        pay_companies = CompanyActiveEmployesLists.objects.filter(company__in=pay_i)
        
        for j in not_pay_companies:
            j_list = str(j.list_employees)
            j_list = j_list.split(" ")
            u = User.objects.filter(pk__in=j_list)
            for f in u:
                f.is_active = False
                f.save()
                
        for j in pay_companies:
            j_list = str(j.list_employees)
            j_list = j_list.split(" ")
            u = User.objects.filter(pk__in=j_list)
            for f in u:
                f.is_active = True
                f.save()
                
        print(f'Автоматическое списание. Не оплачено: {not_pay_i}. Оплачено: {pay_i}')

    def notice_letter(self):
        note_list = Company.objects.filter(payement_date=now)
        for i in note_list:
            user_email = i.manager_email
            subject = f'Скоро наступит дата отправки ЛО в поверку/аттестацию для компании {i.name}'
            email_body = f"Список приборов"
            email(subject, email_body, user_email)
        
    def handle(self, *args, **options):
        self.take_rent()
        self.notice_letter()  # Добавлен вызов метода отправки писем уведомлений
