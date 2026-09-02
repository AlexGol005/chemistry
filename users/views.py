from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management.utils import get_random_secret_key
from django.core.mail import send_mail

# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .forms import UserRegisterForm, UserUdateForm, ProfileUdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from equipment.models import *

from django.views import View
from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from django.views import View
from django.shortcuts import render
from django.core.exceptions import PermissionDenied




# Функция отправки сообщения
def email(subject, content, user_email):
   send_mail(subject,
      content,
      'sandra.005@mail.ru',
     [user_email, 'sandra.005@mail.ru']
   )





from django.contrib import messages
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'users/user.html'

    def form_valid(self, form):
        user = form.get_user()
        
        if hasattr(user, 'profile') and user.profile.userid == 'chem':
            # Добавляем extra_tags='safe', чтобы разрешить HTML внутри сообщения
            messages.error(
                self.request, 
                'Ваша учетная запись пригодна для раздела — Изучение Химии. '
                'Зайдите с <a href="https://xn--h1aal8a3c.site/chem/" style="font-weight:bold; text-decoration:underline;">этой страницы</a>.',
                extra_tags='safe'
            )
            # Возвращаем пользователя обратно на форму логина с выводом этой ошибки
            return self.form_invalid(form) 
            
        # Если проверка пройдена, логиним стандартно
        from django.contrib.auth import login as auth_login
        auth_login(self.request, user) #
        return redirect(self.get_success_url()) #




def HeadEmployeereg(request):
    """выводит форму для добавления первого сотрудника и вместе с ним - профиля компании"""
    """path('heademployeereg/', views.HeadEmployeereg, name='heademployeereg'),"""
    """'users/reg.html'"""
    
    if request.method == "POST":
        group_name = 'Продвинутый пользователь'
        form = UserRegisterForm(request.POST)
        form1 = ProfileRegisterForm(request.POST) 
        if form.is_valid() and form1.is_valid():
            u_f = form.save()
            p_f = form1.save(commit=False)
            p_f.user_id = u_f.id
            
            p_f.userid = get_random_secret_key()
            newuserid =  p_f.userid
            p_f.main_user = True
            p_f.save()  
            u_f.email = p_f.user_email
            u_f.save()
            g = Group.objects.get(name=group_name)
            g.user_set.add(u_f)
            username = form.cleaned_data.get('username')

            user = User.objects.get(pk=u_f.pk)
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save(update_fields=['password'])
                   
            user_email = form1.cleaned_data.get('user_email')
            name_prima = f'"Новая организация пользователя {username}"'

            newcompany = Company.objects.get_or_create(userid=newuserid, pay = False, name=name_prima, name_big=name_prima)

            if user_email:
               subject = f'Сообщение c JL о регистрации нового пользователя'
               email_body = f"Добро пожаловать! Для вас создана учетная запись\n" \
                                f"в базе обслуживания лабораторного обрудования и регистрации микроклимата\n" \
                                f"ссылка для входа:\n" \
                                f"https://www.journallabeq.ru/login/\n" \
                                f"Данные для входа на сайт:\n" \
                                f"логин: {username};\n"\
                                f"пароль: {word}\n"\
                                 f"Вы создали новую организацию. Войдите в Вашу учетную запись и отредактируйте её данные\n"\
                                 f"По всем вопросам обращайтесь к администрации сайта по email sandra.005@mail.ru или по телефону +79500484071 (включая WhatsApp и Viber)"
               
               email(subject, email_body, user_email)
                             
                                 
                               

            messages.success(request, f'Пользовать {username} и {name_prima} были успешно созданы! Пароль для входа выслан на ваш емаил.')
                  
            return redirect('profile')
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            return redirect('heademployeereg')
                
    else:
        form = UserRegisterForm()
        form1 = ProfileRegisterForm()
        data =         {
            'title': 'Страница регистрации',
            'form': form,
            'form1': form1,
        }
        return render(request,  'users/reg.html', data)



class ProfileView(LoginRequiredMixin, TemplateView):
    """выводит персональную страницу """
    template_name = 'users/profile.html'
    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        l = user.groups.values_list('name',flat = True) 
        try:
            user_group = list(l)[0]
        except:
             user_group = 'Суперпользователь'
        try:    
           employees = Employees.objects.filter(userid__userid=user.profile.userid)
           company = Company.objects.get(userid=user.profile.userid)
           context['employees'] = employees
           context['company'] = company 
           context['user_group'] = user_group 
           context['ProfileUdateForm'] = ProfileUdateForm(self.request.POST, self.request.FILES,  instance=self.request.user.profile) 
        except:
           context['company'] = "ф"
            
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if context['ProfileUdateForm'].is_valid() and context['company'] != "ф":
            order = context['ProfileUdateForm'].save(commit=False)
            order.save()
            return redirect('profile')

        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('profile')



class CompanyProfileView(LoginRequiredMixin, TemplateView):
    """выводит страницу данных компании """
    template_name = 'users/companyprofile.html'
    
    def get_context_data(self, **kwargs):
        context = super(CompanyProfileView, self).get_context_data(**kwargs)
        try:
            user = User.objects.get(username=self.request.user)
            if user.is_staff or user.is_superuser:
                context['USER'] = True
            else:
                context['USER'] = False
        except:
            context['USER'] = False
        employees = Employees.objects.filter(userid__userid=user.profile.userid)
        company = Company.objects.get(userid=user.profile.userid)
        context['employees'] = employees
        context['company'] = company 
            
        return context


@login_required
def CompanyUpdateView(request):
    """выводит форму для обновления данных о компании"""
    uruser = request.user
    ruser = request.user.profile.userid
    if uruser.has_perm('equipment.add_equipment') or uruser.is_superuser:
        
        if request.method == "POST":
            form = CompanyCreateForm(request.POST, instance=Company.objects.get(userid=ruser))
            if form.is_valid():

                n = Agreementverification.objects.get_or_create(active=True, company=Company.objects.get(userid=ruser), verificator=Verificators.objects.get(pk=1), pointer=ruser)
                order = form.save(commit=False)
                order.save() 
                               
                return redirect('companyprofile')
        else:
            form = CompanyCreateForm(instance=Company.objects.get(userid=ruser))
        data = {'form': form,}               
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел недоступен')
        return redirect('companyupdate')


class EmployeesView(LoginRequiredMixin, TemplateView):
    """выводит страницу сотрудников компании """
    """path('employees/', UserView.EmployeesView.as_view(), name='employees'),"""
    
    template_name = 'users/employees.html'
    
    def get_context_data(self, **kwargs):
        context = super(EmployeesView, self).get_context_data(**kwargs)
        employees = User.objects.filter(profile__userid=self.request.user.profile.userid)
        company = Company.objects.get(userid=self.request.user.profile.userid)
        context['employees'] = employees
        context['company'] = company             
        return context


class BalanceChangeView(LoginRequiredMixin, TemplateView):
    """выводит страницу данных о платежах и списаниях баланса компании """
    """path('balancechange/', UserView.BalanceChangeView.as_view(), name='balancechange'),"""
    
    template_name = 'users/balancechange.html'
    
    def get_context_data(self, **kwargs):
        context = super(BalanceChangeView, self).get_context_data(**kwargs)
        company = Company.objects.get(userid=self.request.user.profile.userid)
        balancechange = CompanyBalanceChange.objects.filter(company=company).order_by('-pk')
        
        context['balancechange'] = balancechange
        context['company'] = company 
        context['pay'] = monthly_payment
        return context



@login_required
def Employeereg(request):
    """выводит форму для добавления пользователя (сотрудника) и его профиля уже зарегистрированным начальником лаборатории"""
    """path('employeereg/', views.Employeereg, name='employeereg'),"""
    """'users/reg.html'"""
    
    if request.method == "POST":
        group_name = 'Базовый пользователь'
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            form = UserRegisterForm(request.POST)
            form1 = ProfileRegisterForm(request.POST) 
            if form.is_valid() and form1.is_valid():
                u_f = form.save()
                p_f = form1.save(commit=False)
                p_f.user_id = u_f.id
                p_f.userid = request.user.profile.userid
                p_f.save() 
                company = Company.objects.get(userid=request.user.profile.userid)
                au, create = CompanyActiveEmployesLists.objects.get_or_create(company=company)
                if au.list_employees:
                   a = au.list_employees
                   au.list_employees = f'{a} {u_f.pk}'
                   au.save()
                else:
                   au.list_employees = f'{u_f.pk}'
                   au.save()
                   
                g = Group.objects.get(name=group_name)
                g.user_set.add(u_f)
                username = form.cleaned_data.get('username')
               
                user = User.objects.get(pk=u_f.pk)
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save(update_fields=['password'])

               
                u_f.email = p_f.user_email
                u_f.save()
                messages.success(request, f'Пользовать {username} был успешно создан!')
                user_email = form1.cleaned_data.get('user_email')

                if user_email:

                   subject = f'Сообщение c JL о регистрации нового пользователя'
                   email_body = f"Для вас создана учетная запись\n" \
                                f"в базе обслуживания лабораторного обрудования и регистрации микроклимата\n" \
                                f"ссылка для входа:\n" \
                                f"https://www.journallabeq.ru/login/\n" \
                                f"Данные для входа на сайт:\n" \
                                f"логин: {username};\n"\
                                f"пароль: {password}\n"
                   
   
                   email(subject, email_body, user_email)
                   
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save(update_fields=['password'])
                return redirect('employees')
            else:
                messages.add_message(request, messages.ERROR, form.errors)
                return redirect('employees')
                
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect('employees')
    else:
        form = UserRegisterForm()
        form1 = ProfileRegisterForm()
        data =         {
            'title': 'Страница регистрации - Управление Лабораторией',
            'form': form,
            'form1': form1,
        }
        return render(request,  'users/reg.html', data)
        
       
def EmployeeUpdateView(request, str):
    """выводит форму для обновления данных о сотруднике"""
    """path('employeeupdate/<str:str>/', views.EmployeeUpdateView, name='employeeupdate'),"""
    """'users/reg.html'"""
    e=User.objects.get(pk=str)
    a = e.groups.last().name
    activity = e.is_active
    if activity:
        activity = 'деактивировать учетную запись'
    else:
        activity = 'активировать учетную запись'
        
  
    if a == "Базовый пользователь":
        e1 = 'Продвинутый пользователь'
    if a == "Продвинутый пользователь":
        e1 = 'Базовый пользователь'      
   
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            form = UserUdateForm(request.POST, instance=User.objects.get(pk=str))
            form1 = ProfileRegisterForm(request.POST, instance=Profile.objects.get(user__pk=str)) 
                                                          
            if form.is_valid() and form1.is_valid():
                order = form.save(commit=False)
                order1 = form1.save(commit=False)
                order.save()                
                order1.save()
                order.email = order1.user_email
                order.save()
                return redirect('employees')
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect('employees')
    else:
        form = UserUdateForm(instance=User.objects.get(pk=str))
        form1 = ProfileRegisterForm(instance=Profile.objects.get(user__pk=str)) 
     
    data = {'form': form,
                'form1': form1,
                'e': e,
                'e1': e1,
                'a': a,
                'a': a,
            'activity':activity,
               }                
    return render(request, 'users/reg.html', data)



@login_required
def RightsEmployeereg(request, str):
    """выполняет действие изменения группы прав пользователя из фронта сайта со страницы редактирования профиля пользователя"""
    """path('groupchange/<str:str>/', views.RightsEmployeereg, name='groupchange'),"""
    
    instance=User.objects.get(pk=str)
    
    if request.method == 'POST':
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if 'Базовый пользователь' in request.POST:
                add_group_name = 'Продвинутый пользователь'
                rem_group_name = 'Базовый пользователь'
            if 'Продвинутый пользователь' in request.POST:
                add_group_name = 'Базовый пользователь'
                rem_group_name = 'Продвинутый пользователь'
            g_add = Group.objects.get(name=add_group_name)
            g_rem = Group.objects.get(name=rem_group_name)    
            g_add.user_set.add(instance)         
            g_rem.user_set.remove(instance)
            return redirect(reverse('employeeupdate', kwargs={'str': str}))
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect('employees')


@login_required
def Useractivityreg(request, slug):
   """выполняет действие изменения активности пользователя из фронта сайта со страницы редактирования профиля пользователя"""
   """path('useractivity/<slug:slug>/', views.Useractivityreg, name='useractivity'),"""
    
   company = Company.objects.get(userid=request.user.profile.userid) 
   instance=User.objects.get(pk=slug)
   if request.method == 'POST':
      if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
         if 'деактивировать учетную запись' in request.POST:
            instance.is_active = False
            instance.save()
            au = CompanyActiveEmployesLists.objects.get(company=company)
            au_list = str(au.list_employees)
            au_list = au_list.split(" ")
            pk_inst = str(instance.pk)
            au_list.remove(pk_inst)
            a = ' '.join(au_list)
            au.list_employees = a
            au.save()
         if 'активировать учетную запись' in request.POST:
            instance.is_active = True
            instance.save()
            au = CompanyActiveEmployesLists.objects.get(company=company)
            au_list = str(au.list_employees)
            au_list = au_list.split(" ")
            pk_inst = str(instance.pk)
            au_list.append(pk_inst)
            a = ' '.join(au_list)
            au.list_employees = a
            au.save()
      else:
         messages.success(request, 'Раздел доступен только продвинутому пользователю')
         return redirect('employees')
   return redirect(reverse('employeeupdate', kwargs={'str': slug}))
    


class ChemProfileView(LoginRequiredMixin, TemplateView):
    """выводит персональную страницу изучение химии """
    template_name = 'users/chemprofile.html'
    def get_context_data(self, **kwargs):
        context = super(ChemProfileView, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        context['ChemProfileUdateForm'] = ChemProfileUdateForm(self.request.POST, self.request.FILES,  instance=self.request.user.profile) 
            
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if context['ChemProfileUdateForm'].is_valid():
            order = context['ChemProfileUdateForm'].save(commit=False)
            order.save()
            return redirect('chemprofile')

        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('chemprofile')


def Chemprofilereg(request):
    """Выводит форму для регистрации изучающего химию"""
    if request.method == "POST":
        form = ChemUserRegisterForm(request.POST)
        form1 = ChemProfileRegisterForm(request.POST) 
        
        if form.is_valid() and form1.is_valid():
            # 1. Сохраняем основного пользователя
            user = form.save()
            
            # 2. Добавляем пользователя в группу (если это необходимо)
            group, created = Group.objects.get_or_create(name='Базовый пользователь')
            user.groups.add(group)
            
            # 3. Подготавливаем профиль, но не сохраняем сразу
            profile = form1.save(commit=False)
            
            # 4. СВЯЗЫВАЕМ профиль с только что созданным пользователем
            profile.user = user  # Предполагается, что в модели Profile есть поле user
            
            # 5. Теперь сохраняем профиль в базу данных
            profile.save()
            
            messages.success(request, 'Пользователь успешно создан!')
            return redirect('chem')
        else:
            # Если формы невалидны, лучше не делать редирект, 
            # чтобы пользователь увидел ошибки валидации прямо в полях
            messages.error(request, 'Ошибка при регистрации. Проверьте введенные данные.')
    else:
        form = ChemUserRegisterForm()
        form1 = ChemProfileRegisterForm()

    data = {
        'title': 'Страница регистрации - изучение химии',
        'form': form,
        'form1': form1,
    }
    return render(request, 'users/chemreg.html', data)
