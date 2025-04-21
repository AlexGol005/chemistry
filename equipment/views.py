"""
Модуль проекта LabJournal, приложения equipment.
Приложение equipment это обширное приложение, включает все про лабораторное оборудование и лабораторные помещения
Данный модуль views.py выводит представления для вывода форм и информации.
Список блоков:
блок 0 - заказ поверки
блок 1 - заглавные страницы с кнопками, структурирующие разделы. (Самая верхняя страница - записана в приложении main)
блок 2 - списки и обновление: комнаты, поверители, производители
блок 3 - списки: Все оборудование, СИ, ИО, ВО, госреестры, характеристики ИО, характеристики ВО
блок 4 - формы регистрации и обновления: комнаты, поверители, производители  и поверители, договоры с поверителями
блок 5 - микроклимат: журналы, формы регистрации
блок 6 - регистрация госреестры, характеристики, ЛО - внесение, обновление
блок 7 - все поисковики
блок 8 - принадлежности к оборудованию
блок 9 - внесение и обновление поверка и аттестация
блок 10 - индивидуальные страницы СИ ИО ВО 
блок 11 - все комментарии ко всему
блок 12 - вывод списков и форм  для метрологического  обеспечения
блок 13 - ТОиР
блок 14 - все кнопки удаления объектов
блок 15 - массовая загрузка через EXEL
"""
import os
import sys
import pytils.translit
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, request
from django.db.models import Max, Q, Value, CharField, Count, Sum
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse, request
from django_currentuser.middleware import (
get_current_user, get_current_authenticated_user)
import xlrd

from equipment.constants import servicedesc0
from equipment.forms import*
from equipment.models import*
from formstandart import *
from functstandart import get_dateformat, get_rid_point, get_dateformat_django
from .function_for_equipmentapp import get_exnumber
from users.models import Profile, Company

URL = 'equipment'
now = date.today()

def TEST(request):
    """ для тестов """
# path('test/', views.TEST, name='test'),
    
    # l = []
    # for f in MeasurEquipmentCharakters._meta.get_fields():
    #     try:
    #         l.append(f.verbose_name)
    #     except:
    #         pass
            
    # headers = dict()
    # for column in range(len(l)):
    #     value = l[column]
    #     headers[column] = value
    # object = headers
    # object = f'{len(l)} = {len(m)}'
    # l = []
    # m = []
    # for f in MeasurEquipmentCharakters._meta.get_fields():
    #     try:
    #         l.append(f.verbose_name)
    #         m.append(f.name)
    #     except:
    #         pass
    ruser=request.user.profile.userid
    company = Company.objects.get(userid=request.user.profile.userid)
    # note = Activeveraqq.objects.get(pointer=ruser)
    # exelnumber = note.aqq.verificator.companyName
    # exelnumber = pytils.translit.translify(exelnumber)
    # object = str(exelnumber).replace('"', '_').replace(' ', '_').replace('«', '_').replace('»', '_').replace('\'', '_').replace('.', '_').replace('-', '_')
    n = 'К0001'
    n = n + '_' + str(company.pk)
    a=TestingEquipment.objects.filter(pointer=ruser).get(equipment__exnumber=n)
    object = f'{n} and {a}'
    return render(
        request,
        'equipment/e.html',
        {
            'object': object
        })




class OrderVerificationView(LoginRequiredMixin, View):
    """ выводит страницу для заказа и/аттестации """
    """'/orderverification.html'"""
    """path('orderverification/<str:str>/', views.OrderVerificationView.as_view(), name='orderverification'),"""
    
    CHOISE_LIST = [('все приборы', 'все приборы'),('не поверено на сегодняшний день','не поверено на сегодняшний день'), ('требует и на сегодняшний день','требует и на сегодняшний день'), 
               ('нужно заказать замену на сегодняшний день','нужно заказать замену на сегодняшний день'), ('а заказана', 'а заказана')]
    
    def get(self, request, str):
        ruser=request.user.profile.userid
        serdate = request.GET.get('date')
        if not serdate:
           serdate = now
        form = ActivaqqchangeForm(ruser, instance=Activeveraqq.objects.get(pointer=ruser), initial={'ruser': ruser,})
        dateform = DateForm(initial={'date': serdate,})
        i=str
        if i=='0':
            list = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(measurequipment__pk__isnull=False)| Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(testingequipment__pk__isnull=False) 
        if i=='4':
            list = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(measurequipment__newhaveorder=True)| Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(testingequipment__newhaveorder=True) 
        if i=='1':
            list = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(measurequipment__newdatedead_date__lte=serdate) | Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(testingequipment__newdatedead_date__lte=serdate)
        if i=='2':
            list = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(measurequipment__newdateorder_date__lte=serdate) | Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(testingequipment__newdateorder_date__lte=serdate)
        if i=='3':
            list = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(measurequipment__newdateordernew_date__lte=serdate) | Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(testingequipment__newdateordernew_date__lte=serdate)
  
        context = {
            'form': form,
            'dateform': dateform,
            'list': list,
            'ruser':ruser,
            'str':str,
        }
        template_name = URL + '/orderverification.html'
        return render(request, template_name, context)

    def post(self, request, str, *args, **kwargs):
        """выбираем активный договор с поверителем"""
        ruser=request.user.profile.userid
        form = ActivaqqchangeForm(ruser, request.POST, instance=Activeveraqq.objects.get(pointer=ruser), initial={'ruser': ruser,})
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect(f'/equipment/orderverification/{str}/')

        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/orderverification/0/')


@login_required
def OrderVerificationchange(request, str):
    """ на странице для заказа и/аттестации выполняет действие изменения отмеченных объектов и выгрузки заявки на поверку """
    """ никаких страниц эта вьюшка не формирует! """
    """path('orderverificationchange/<str:str>/', views.OrderVerificationchange, name='orderverificationchange'),"""
    
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == 'POST':
            if 'true' in request.POST:
                object_ids = request.POST.getlist('my_object')         
                note = Equipment.objects.filter(id__in=object_ids) 
                for i in note:
                    if i.kategory == 'СИ':               
                        i.measurequipment.newhaveorder = True
                        i.measurequipment.save()
                    elif i.kategory == 'ИО':               
                        i.testingequipment.newhaveorder=True
                        i.testingequipment.save()  
                
                try:
                    # note = Activeveraqq.objects.get(pointer=ruser)
                    # exelnumber = note.aqq.verificator.pk
                    # exelname = f'export_orderverification_{exelnumber}_xls'            
                    # return redirect(exelname, {'object_ids': object_ids})
                    note = Activeveraqq.objects.get(pointer=ruser)

                    exelnumber = note.aqq.verificator.companyName
                    exelnumber = pytils.translit.translify(exelnumber)
                    exelnumber = exelnumber.replace('"', '_').replace(' ', '_').replace('«', '_').replace('»', '_').replace('\'', '_').replace('.', '_').replace('-', '_')
                    exelname = f'export_orderverification_{exelnumber}_xls'
                    return redirect(exelname, {'object_ids': object_ids})
                except:
                    # raise
                    return redirect('export_orderverification_xls', {'object_ids': object_ids})
                        
            if 'false' in request.POST:
                object_ids = request.POST.getlist('my_object')
                note = Equipment.objects.filter(id__in=object_ids) 
                for i in note:
                    if i.kategory == 'СИ':               
                        i.measurequipment.newhaveorder=False
                        i.measurequipment.save()
                    elif i.kategory == 'ИО':               
                        i.testingequipment.newhaveorder=False
                        i.testingequipment.save()
                return redirect(f'/equipment/orderverification/{str}/')
    else:
        messages.success(request, "Раздел доступен только продвинутому пользователю")
        return redirect('/equipment/orderverification/0/')

       

# блок 1 - заглавные страницы с кнопками, структурирующие разделы. Самая верхняя страница - в приложении main

class VerificationDocs(LoginRequiredMixin, TemplateView):
    """выводит страницу для выгрузки документов после поверки"""
    """path('verificationdocs/', views.VerificationDocs.as_view(), name='verificationdocs'),"""
    
    template_name = URL + '/verificationdocs.html'

class ManagerEquipmentView(LoginRequiredMixin, TemplateView):
    """выводит страницу для управляющего оборудованием"""
    """кнопка не показывается базовому пользователю"""
    """path('managerequipment/', views.ManagerEquipmentView.as_view(), name='managerequipment'),"""
    
    template_name = URL + '/manager.html'


class MeteorologicalParametersView(LoginRequiredMixin, ListView):
    """Выводит страницу с кнопками для добавления помещений, микроклимата и вывода журнала микроклимата"""
    """path('meteo/', views.MeteorologicalParametersView.as_view(), name='meteo'),"""
    
    template_name = URL + '/meteo.html'
    context_object_name = 'objects'

    def get_queryset(self):
        queryset = Rooms.objects.filter(pointer=self.request.user.profile.userid)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MeteorologicalParametersView, self).get_context_data(**kwargs)
        context['form'] = DateForm()
        return context


class MetrologicalEnsuringView(LoginRequiredMixin, TemplateView):
    """Выводит заглавную страницу для Этикетки о е/аттестации и списки на у/аттестацию """
    template_name = URL + '/metro.html'
    """path('metro/', views.MetrologicalEnsuringView.as_view(), name='metro'),"""

    def get_context_data(self, **kwargs):
        context = super(MetrologicalEnsuringView, self).get_context_data(**kwargs)
        context['form'] = DateForm()
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    """Выводит страницу с кнопками для вывода планов и отчётов по оборудованию"""
    """path('reports/', views.ReportsView.as_view(), name='reports'),"""
    
    template_name = URL + '/reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = YearForm()
        return context



# блок 2 - списки: комнаты, поверители, производители

class ManufacturerView(ListView):
    """ Выводит список всех производителей """
    """path('manufacturerlist/', views.ManufacturerView.as_view(), name='manufacturerlist'),"""
    
    model = Manufacturer
    template_name = URL + '/manufacturer_list.html'
    context_object_name = 'objects'
    ordering = ['companyName']
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ManufacturerView, self).get_context_data(**kwargs)
        context['POINTER'] = self.request.user.profile.userid
        context['serform'] = Searchtestingform
        return context


class VerificatorsCreationView(LoginRequiredMixin,  ListView):
    """ выводит список поверителей """
    """path('verificatorsreg/', views.VerificatorsCreationView.as_view(), name='verificatorsreg'),"""
    
    template_name = URL + '/verificators_list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(VerificatorsCreationView, self).get_context_data(**kwargs)
        context['title'] = 'Внести организацию поверителя'
        context['serform'] = Searchtestingform
        context['POINTER'] = self.request.user.profile.userid
        
        return context

    def get_queryset(self):
        queryset = Verificators.objects.exclude(companyName='Не указан')
        return queryset


class RoomsView(LoginRequiredMixin, TemplateView):
    """выводит страницу комнат компании """
    """path('rooms/', views.RoomsView.as_view(), name='rooms'),"""
    
    template_name = 'equipment/rooms.html'
    def get_context_data(self, **kwargs):
        context = super(RoomsView, self).get_context_data(**kwargs)
        rooms = Rooms.objects.filter(pointer=self.request.user.profile.userid)
        company = Company.objects.get(userid=self.request.user.profile.userid)
        context['rooms'] = rooms
        context['company'] = company 
        return context


class AgreementVerificators(LoginRequiredMixin, TemplateView):
    """выводит страницу договоров с поверителями компании """
    """path('agreementcompanylist', views.AgreementVerificators.as_view(), name='agreementcompanylist'),"""
    
    template_name = 'equipment/veragreements.html'
    
    def get_context_data(self, **kwargs):
        context = super(AgreementVerificators, self).get_context_data(**kwargs)
        company = Company.objects.get(userid=self.request.user.profile.userid)
        objects = Agreementverification.objects.filter(company=company).exclude(verificator__companyName='Не указан')
        context['company'] = company 
        context['objects'] = objects
        context['POINTER'] = self.request.user.profile.userid
        return context
        

@login_required
def RoomsUpdateView(request, str):
    """выводит форму для обновления данных о помещении"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = RoomsUpdateForm(ruser, request.POST, instance=Rooms.objects.get(pk=str), initial={'ruser': ruser,})                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('rooms')
        else:
            form = RoomsUpdateForm(ruser, instance=Rooms.objects.get(pk=str), initial={'ruser': ruser,})
        data = {'form': form,}                
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('rooms')



# блок 3 - списки: Все оборудование, СИ, ИО, ВО, госреестры, характеристики ИО, характеристики ВО


class EquipmentAllView(LoginRequiredMixin, ListView):
    """ Выводит список Всего ЛО"""
    """ path('euipmentall/', views.EquipmentAllView.as_view(), name='euipmentall'),"""
    template_name = URL + '/EquipmentLIST.html'
    context_object_name = 'objects'  
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(EquipmentAllView, self).get_context_data(**kwargs)
        context['form'] = SearchEqForm()
        return context

    def get_queryset(self):
        queryset = Equipment.objects.filter(pointer=self.request.user.profile.userid).order_by('-pk')
        return queryset



class MeasurEquipmentCharaktersView(LoginRequiredMixin, ListView):
    """ Выводит список госреестров """
    """path('measurequipmentcharacterslist/', views.MeasurEquipmentCharaktersView.as_view(), name='measurequipmentcharacterslist'),"""
    
    template_name = URL + '/MEcharacterslist.html'
    context_object_name = 'objects'
    ordering = ['reestr']
    paginate_by = 12

    def get_queryset(self):
        queryset = MeasurEquipmentCharakters.objects.filter(pointer=self.request.user.profile.userid)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MeasurEquipmentCharaktersView, self).get_context_data(**kwargs)
        context['form'] = Searchreestrform()
        context['title'] = 'Госреестры, типы, модификации средств измерений'
        context['POINTER'] = self.request.user.profile.userid
        user = User.objects.get(username=self.request.user)
        return context


class TestingEquipmentCharaktersView(LoginRequiredMixin, ListView):
    """ Выводит список характеристик ИО """
    template_name = URL + '/TEcharacterslist.html'
    context_object_name = 'objects'
    ordering = ['name']
    paginate_by = 12

    def get_queryset(self):
        queryset = TestingEquipmentCharakters.objects.filter(pointer=self.request.user.profile.userid)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TestingEquipmentCharaktersView, self).get_context_data(**kwargs)
        context['form'] = Searchtestingform()
        context['title'] = 'Характеристики, типы, испытательного оборудования'
        context['POINTER'] = self.request.user.profile.userid
        user = User.objects.get(username=self.request.user)
        return context


class HelpingEquipmentCharaktersView(LoginRequiredMixin, ListView):
    """ Выводит список характеристик ВО """
    template_name = URL + '/HEcharacterslist.html'
    context_object_name = 'objects'
    ordering = ['name']
    paginate_by = 12

    def get_queryset(self):
        queryset = HelpingEquipmentCharakters.objects.filter(pointer=self.request.user.profile.userid)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HelpingEquipmentCharaktersView, self).get_context_data(**kwargs)
        context['form'] = Searchtestingform()
        context['title'] = 'Характеристики, типы, вспомогательного оборудования'
        context['POINTER'] = self.request.user.profile.userid
        user = User.objects.get(username=self.request.user)
        return context


class MeasurEquipmentView(LoginRequiredMixin, ListView):
    """Выводит список средств измерений"""
    template_name = URL + '/MEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']
    paginate_by = 12

    def get_queryset(self):
        queryset = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).exclude(equipment__status='С')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MeasurEquipmentView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context


class TestingEquipmentView(LoginRequiredMixin, ListView):
    """ Выводит список испытательного оборудования """
    template_name = URL + '/TEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters__name']
    paginate_by = 12

    def get_queryset(self):
        queryset = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).exclude(equipment__status='С')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TestingEquipmentView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context


class HelpingEquipmentView(LoginRequiredMixin, ListView):
    """ Выводит список вспомогательного оборудования """
    template_name = URL + '/HEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters__name']
    paginate_by = 12

    def get_queryset(self):
        queryset = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).exclude(equipment__status='С')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HelpingEquipmentView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

class MeasurEquipmentCharaktersStrView(TemplateView):
    """выводит индивидуальную страницу с описанием характеристик СИ """
    """path('mecharaktersstr/<str:str>/', views.MeasurEquipmentCharaktersStrView.as_view(), name='mecharaktersstr'),"""
    
    template_name = URL + '/charaktersstr.html'

    def get_context_data(self, str, **kwargs):
        context = super(MeasurEquipmentCharaktersStrView, self).get_context_data(**kwargs)
        context['obj'] = MeasurEquipmentCharakters.objects.get(pk=str)
        context['modelname'] = 1
        return context


class TestingEquipmentCharaktersStrView(TemplateView):
    """выводит индивидуальную страницу с описанием характеристик ИО """
    template_name = URL + '/charaktersstr.html'

    def get_context_data(self, str, **kwargs):
        context = super(TestingEquipmentCharaktersStrView, self).get_context_data(**kwargs)
        context['obj'] = TestingEquipmentCharakters.objects.get(pk=str)
        context['modelname'] = 2
        return context


class HelpingEquipmentCharaktersStrView(TemplateView):
    """выводит индивидуальную страницу с описанием характеристик ВО """
    template_name = URL + '/charaktersstr.html'

    def get_context_data(self, str, **kwargs):
        context = super(HelpingEquipmentCharaktersStrView, self).get_context_data(**kwargs)
        context['obj'] = HelpingEquipmentCharakters.objects.get(pk=str)
        context['modelname'] = 3
        return context



# блок 4 - формы регистрации и обновления: комнаты, поверители, производители плюс список поверителей и производителей, договоры с поверителями

@login_required
def RoomsCreateView(request):
    """ выводит форму добавления помещения """
    template_name = URL + '/newroomreg.html'
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = RoomsCreateForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    order = form.save(commit=False)
                    order.pointer = request.user.profile.userid
                    order.save()
                    messages.success(request, "Помещение успешно добавлено")
                    return redirect('rooms')
                except: 
                    messages.success(request, 'Эта комната уже есть')
                    return redirect('roomreg')                  
            else:
                messages.success(request, 'Эта комната уже есть')
                return redirect('roomreg')
        else:
            form = RoomsCreateForm()
        data = {'form': form, }                   
        return render(request, template_name, data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('roomreg')


class ManufacturerRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму добавления производителя """
    """path('manufacturerreg/', views.ManufacturerRegView.as_view(), name='manufacturerreg'),"""
    
    template_name = URL + '/reg.html'
    form_class = ManufacturerCreateForm
    success_url = '/equipment/manufacturerlist/'
    success_message = "Производитель успешно добавлен"

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.pointer = self.request.user.profile.userid
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('manufacturerreg')

    def get_context_data(self, **kwargs):
        context = super(ManufacturerRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить производителя ЛО'
        context['POINTER'] = self.request.user.profile.userid
        context['url_title'] = 'equipment/manufacturerlist/'
        return context


class VerificatorRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму добавления поверителя """
    """path('companyverreg/', views.VerificatorRegView.as_view(), name='companyverreg'),"""
    
    template_name = URL + '/reg.html'
    form_class = VerificatorsCreationForm
    success_url = '/equipment/verificatorsreg/'
    success_message = "Поверитель успешно добавлен"

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.pointer = self.request.user.profile.userid
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('companyverreg')

    def get_context_data(self, **kwargs):
        context = super(VerificatorRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить компанию-поверителя ЛО'
        context['url_title'] = '/equipment/agreementcompanylist'
        context['POINTER'] = self.request.user.profile.userid
        context['url_title'] = 'equipment/verificatorsreg/'
        return context


class AgreementVerificatorRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму добавления договора с поверителем """
    """  path('agreementcompanyverreg/', views.AgreementVerificatorRegView.as_view(), name='agreementcompanyverreg'),   """
 
    template_name = URL + '/veragreementreg.html'
    form_class = AgreementVerificatorsCreationForm
    success_url = '/equipment/agreementcompanylist'
    success_message = "Договор с поверителем успешно добавлен"

    def get_context_data(self, **kwargs):
        context = super(AgreementVerificatorRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить договор с компанией-поверителем ЛО'
        context['POINTER'] = self.request.user.profile.userid
        return context

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.company = Company.objects.get(userid=self.request.user.profile.userid)
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/verificatorsreg/')


@login_required
def AgreementVerificatorUpdateView(request, str):
    """выводит форму для обновления договора с поверителем"""
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = AgreementVerificatorsCreationForm(request.POST, instance=Agreementverification.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('/equipment/agreementcompanylist')
        else:
            form = AgreementVerificatorsCreationForm(instance=Agreementverification.objects.get(pk=str))
        data = {'form': form,}                
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/agreementcompanylist')


@login_required
def VerificatorUpdateView(request, str):
    """выводит форму для обновления организации-поверителя"""
    """path('verupdate/<str:str>/', views.VerificatorUpdateView, name='verupdate'),"""
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = VerificatorsCreationForm(request.POST, instance= Verificators.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('/equipment/verificatorsreg')
        else:
            form = VerificatorsCreationForm(instance= Verificators.objects.get(pk=str))
        data = {'form': form,}                
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/verificatorsreg')


@login_required
def ManufacturerUpdateView(request, str):
    """выводит форму для обновления организации-производителя"""
    """path('manufupdate/<str:str>/', views.ManufacturerUpdateView, name='manufupdate'),"""
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = ManufacturerCreateForm(request.POST, instance= Manufacturer.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('/equipment/manufacturerlist')
        else:
            form = ManufacturerCreateForm(instance= Manufacturer.objects.get(pk=str))
        data = {'form': form,}                
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/manufacturerlist')


class PersonchangeFormView(LoginRequiredMixin, View):
    """вывод формы смены ответсвенного за прибор, URL=personchangereg/<str:str>/"""
    def get(self, request, str):
        ruser=request.user.profile.userid
        title = 'Смена ответственного за прибор'
        dop = Equipment.objects.get(exnumber=str)
        form =  PersonchangeForm(ruser, initial={'ruser': ruser,})
        context = {
            'title': title,
            'dop': dop,
            'form': form,
        }
        template_name = 'equipment/reg.html'
        return render(request, template_name, context)

    def post(self, request, str, *args, **kwargs):
        ruser=request.user.profile.userid
        form = PersonchangeForm(ruser, request.POST)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=str)
                order.save()
                if order.equipment.kategory == 'СИ':
                    return redirect(f'/equipment/measureequipment/{str}')
                if order.equipment.kategory == 'ИО':
                    return redirect(f'/equipment/testequipment/{self.kwargs["str"]}')
                if order.equipment.kategory == 'ВО':
                    return redirect(f'/equipment/helpequipment/{self.kwargs["str"]}')
        else:
            messages.success(request, f'Раздел доступен только продвинутому пользователю')
            if order.equipment.kategory == 'СИ':
                return redirect(f'/equipment/measureequipment/{str}')
            if order.equipment.kategory == 'ИО':
                return redirect(f'/equipment/testequipment/{self.kwargs["str"]}')
            if order.equipment.kategory == 'ВО':
                return redirect(f'/equipment/helpequipment/{self.kwargs["str"]}')


class RoomschangeFormView(LoginRequiredMixin, View):
    """вывод формы смены помещения, URL=roomschangereg/<str:str>/"""
    def get(self, request, str):
        ruser=request.user.profile.userid
        title = 'Смена размещения прибора'
        dop = Equipment.objects.get(exnumber=str)
        form =  RoomschangeForm(ruser, initial={'ruser': ruser,})
        context = {
            'title': title,
            'dop': dop,
            'form': form,
        }
        template_name = 'equipment/roomreg.html'
        return render(request, template_name, context)

    def post(self, request, str, *args, **kwargs):
        ruser=request.user.profile.userid
        form = RoomschangeForm(ruser, request.POST)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=str)
                order.save()
                if order.equipment.kategory == 'СИ':
                    return redirect(f'/equipment/measureequipment/{str}')
                if order.equipment.kategory == 'ИО':
                    return redirect(f'/equipment/testequipment/{self.kwargs["str"]}')
                if order.equipment.kategory == 'ВО':
                    return redirect(f'/equipment/helpequipment/{self.kwargs["str"]}')
        else:
            messages.success(request, f'Раздел доступен только продвинутому пользователю')
            if order.equipment.kategory == 'СИ':
                return redirect(f'/equipment/measureequipment/{str}')
            if order.equipment.kategory == 'ИО':
                return redirect(f'/equipment/testequipment/{self.kwargs["str"]}')
            if order.equipment.kategory == 'ВО':
                return redirect(f'/equipment/helpequipment/{self.kwargs["str"]}')


class PersonchangeView(LoginRequiredMixin, ListView):
    """Выводит страницу с историей изменения ответственных за прибор для конкретного прибора"""
    """path('personchangelist/<str:str>/', views.PersonchangeView.as_view(), name='personchangelist'),"""
    
    template_name = URL + '/Epersonchangelist.html'
    context_object_name = 'objects'

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = Personchange.objects.filter(equipment__pk=str)
        return queryset

    def get_context_data(self, **kwargs):
        str=self.kwargs['str']
        context = super(PersonchangeView, self).get_context_data(**kwargs)
        eq = Personchange.objects.filter(equipment__pk=str).last().equipment
        context['eq'] = eq
        return context



class RoomchangeView(LoginRequiredMixin, ListView):
    """Выводит страницу с историей изменения расположения для конкретного прибора"""
    """path('roomchangelist/<str:str>/', views.RoomchangeView.as_view(), name='roomchangelist'),"""
    
    template_name = URL + '/Eroomchangelist.html'
    context_object_name = 'objects'

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = Roomschange.objects.filter(equipment__pk=str)
        return queryset

    def get_context_data(self, **kwargs):
        str=self.kwargs['str']
        context = super(RoomchangeView, self).get_context_data(**kwargs)
        eq = Roomschange.objects.filter(equipment__pk=str).last().equipment
        context['eq'] = eq
        return context


# блок 5 - микроклимат: журналы, формы регистрации

class MeteorologicalParametersCreateView(LoginRequiredMixin, SuccessMessageMixin, View):
    """ выводит форму добавления условий микроклимата """
    def get(self, request):
        ruser=request.user.profile.userid
        title = 'Добавить условия окружающей среды'
        dopin = 'equipment/meteo/'
        form =  MeteorologicalParametersRegForm(ruser, initial={'ruser': ruser,})
        context = {
            'title': title,
            'dopin': dopin,
            'form': form,
        }
        template_name = URL + '/reg.html'
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        ruser=request.user.profile.userid
        form = MeteorologicalParametersRegForm(ruser, request.POST, initial={'ruser': ruser,})
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            try:
                if form.is_valid():
                    order = form.save(commit=False)
                    order.save()
                    str = order.roomnumber.pk
                    return redirect(f'/equipment/meteoroom/{str}/') 
                else:
                    messages.success(request, f'Условия уже добавлены ранее')
                    return redirect(f'/equipment/meteoreg/')
            except:
                messages.success(request, f'Сначала добавьте барометр, гигрометр и ответственное лицо для комнаты')
                return redirect(f'/equipment/meteoreg/')
                
        else:
            messages.success(request, f'Раздел доступен только продвинутому пользователю')
            return redirect(f'/equipment/meteoreg/')


class MeteorologicalParametersRoomView(LoginRequiredMixin, ListView):
    """ выводит условия микроклимата и кнопки для добавления и выгрузки для отдельного помещения """
    model = MeteorologicalParameters
    template_name = URL + '/meteoroom.html'
    context_object_name = 'objects'
    paginate_by = 22

    def get_queryset(self):
        queryset = MeteorologicalParameters.objects.filter(roomnumber_id=self.kwargs['pk']).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MeteorologicalParametersRoomView, self).get_context_data(**kwargs)
        try:
            user = User.objects.get(username=self.request.user)
            if user.is_staff:
                context['USER'] = True
            if not user.is_staff:
                context['USER'] = False
        except:
            context['USER'] = False
        get_eq = MeteorologicalParameters.objects.filter(roomnumber=Rooms.objects.get(id=self.kwargs['pk']).pk).last()
        try:
            context['me'] = get_eq.equipments 
        except:
            context['me'] = 'добавьте средства измерения для комнаты и  первую запись о условиях микроклимата'
        try:
            context['rp'] = get_eq.person 
        except:
            context['rp'] = 'добавьте ответственного для комнаты и  первую запись о условиях микроклимата'
        context['title'] = Rooms.objects.get(id=self.kwargs['pk']).roomnumber
        context['titlepk'] = Rooms.objects.get(id=self.kwargs['pk']).pk
        context['form'] = DateForm()
        context['form1'] = YearForm(initial={'date': now.year})
        return context


class MeteorologicalParametersRoomSearchResultView(ListView):
    # path('meteoroomser/<int:pk>/', views.MeteorologicalParametersRoomSearchResultView.as_view(), name='meteoroomser')
    """показывает результаты поиска Найти условия микроклимата на дату:"""
    
    model = MeteorologicalParameters
    template_name = URL + '/meteoroom.html'
    context_object_name = 'objects'
    paginate_by = 22

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset1 = MeteorologicalParameters.objects.filter(roomnumber_id=self.kwargs['pk'])
        queryset = queryset1.filter(date=serdate)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MeteorologicalParametersRoomSearchResultView, self).get_context_data(**kwargs)
        serdate = self.request.GET['date']
        context['title'] = Rooms.objects.get(id=self.kwargs['pk']).roomnumber
        context['titlepk'] = Rooms.objects.get(id=self.kwargs['pk']).pk
        context['form'] = DateForm(initial={'date': serdate})
        context['form1'] = YearForm(initial={'date': now.year})
        return context



# блок 6 - регистрация госреестры, характеристики, ЛО - внесение, обновление

@login_required
def EquipmentReg(request):
    """выводит форму для регистрации  ЛО"""
    """path('equipmentreg/', views.EquipmentReg, name='equipmentreg'),"""
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = EquipmentCreateForm(request.POST, request.FILES)
            try:
                if form.is_valid():
                    order = form.save(commit=False)
                    order.pointer = request.user.profile.userid
                    have_exnumber = order.exnumber                
                    pointer = order.pointer
                    order.exnumber = get_exnumber(have_exnumber, pointer)
                    order.save()
                    if order.kategory == 'СИ':
                        return redirect(f'/equipment/measureequipmentreg/{order.exnumber}/')
                    if order.kategory == 'ИО':
                        return redirect(f'/equipment/testequipmentreg/{order.exnumber}/')
                    if order.kategory == 'ВО':
                        return redirect(f'/equipment/helpequipmentreg/{order.exnumber}/')
                    else:
                        return redirect('equipmentlist')
                else:
                    messages.success(request, 'Заполните поле "Производитель прибора"')                    
            except:                
                messages.success(request, 'Прибор с таким заводским номером и от этого производителя уже существует! Добавьте "0" к заводскому номеру"')
                return redirect('/equipment/equipmentreg/')
        else:
            form = EquipmentCreateForm()
            content = {
                'form': form,
                    }
            return render(request, 'equipment/Equipmentreg.html', content)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/')


class MeasurEquipmentCharaktersRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму внесения госреестра. """
    """path('measurequipmentcharactersreg/', views.MeasurEquipmentCharaktersRegView.as_view(), name='measurequipmentcharactersreg'),"""
    
    template_name = URL + '/Echaractersreg.html'
    form_class = MeasurEquipmentCharaktersCreateForm
    success_url = '/equipment/measurequipmentcharacterslist/'
    success_message = "Госреестр успешно добавлен!"
    error_message = "Раздел доступен только продвинутому пользователю"

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.pointer = self.request.user.profile.userid
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/measurequipmentcharacterslist/')

    def get_context_data(self, **kwargs):
        context = super(MeasurEquipmentCharaktersRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить госреестр'
        context['dopin'] = 'equipment/measurequipmentcharacterslist'
        return context


@login_required
def MeasurEquipmentCharaktersUpdateView(request, str):
    """выводит форму для обновления данных о госреестре"""
    """path('measurequipmentcharactersupdate/<str:str>/', views.MeasurEquipmentCharaktersUpdateView, name='measurequipmentcharactersupdate'),"""

    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = MeasurEquipmentCharaktersUpdateForm(request.POST,
                                                       instance=MeasurEquipmentCharakters.objects.get(pk=str))
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('measurequipmentcharacterslist')
        else:
            form = MeasurEquipmentCharaktersUpdateForm(instance=MeasurEquipmentCharakters.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/Echaractersreg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/measurequipmentcharacterslist/')


class TestingEquipmentCharaktersRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму внесения характеристик ИО. """
    """path('testingequipmentcharactersreg/', views.TestingEquipmentCharaktersRegView.as_view(), name='testingequipmentcharactersreg'),"""
    
    template_name = URL + '/Echaractersreg.html'
    form_class = TestingEquipmentCharaktersCreateForm
    success_url = '/equipment/testingequipmentcharacterslist/'
    success_message = "Характеристики ИО успешно добавлены"
    error_message = "Раздел доступен только продвинутому пользователю"

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.pointer = self.request.user.profile.userid
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/testingequipmentcharacterslist/')

    def get_context_data(self, **kwargs):
        context = super(TestingEquipmentCharaktersRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить характеристики ИО'
        context['dopin'] = 'equipment/testingequipmentcharacterslist'
        return context


@login_required
def TestingEquipmentCharaktersUpdateView(request, str):
    """выводит форму для обновления данных о характеристиках ИО"""
    """path('testequipmentcharactersupdate/<str:str>/', views.TestingEquipmentCharaktersUpdateView, name='testequipmentcharactersupdate'),"""
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = TestingEquipmentCharaktersUpdateForm(request.POST,
                                                       instance=TestingEquipmentCharakters.objects.get(pk=str))
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('testingequipmentcharacterslist')
        else:
            form = TestingEquipmentCharaktersUpdateForm(instance=TestingEquipmentCharakters.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/Echaractersreg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/testingequipmentcharacterslist/')


class HelpingEquipmentCharaktersRegView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ выводит форму внесения характеристик ВО. """
    """path('helpingequipmentcharactersreg/', views.HelpingEquipmentCharaktersRegView.as_view(), name='helpingequipmentcharactersreg'),"""
    
    template_name = URL + '/Echaractersreg.html'
    form_class = HelpingEquipmentCharaktersCreateForm
    success_url = '/equipment/helpingequipmentcharacterslist/'
    success_message = "Характеристики ВО успешно добавлены"
    error_message = "Раздел доступен только продвинутому пользователю"

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.pointer = self.request.user.profile.userid
            order.save()
            return super().form_valid(form)
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/helpingequipmentcharacterslist/')

    def get_context_data(self, **kwargs):
        context = super(HelpingEquipmentCharaktersRegView, self).get_context_data(**kwargs)
        context['title'] = 'Добавить характеристики ВО'
        context['dopin'] = 'equipment/helpingequipmentcharacterslist'
        return context


@login_required
def HelpingEquipmentCharaktersUpdateView(request, str):
    """выводит форму для обновления данных о характеристиках ВО"""
    """ path('helpequipmentcharactersupdate/<str:str>/', views.HelpingEquipmentCharaktersUpdateView, name='helpequipmentcharactersupdate'),"""
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = HelpingEquipmentCharaktersUpdateForm(request.POST,
                                                       instance=HelpingEquipmentCharakters.objects.get(pk=str))
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect('helpingequipmentcharacterslist')
        else:
            form = HelpingEquipmentCharaktersUpdateForm(instance=HelpingEquipmentCharakters.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/Echaractersreg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('/equipment/helpingequipmentcharacterslist/')


class MeasureequipmentregView(LoginRequiredMixin, CreateView):
    """ выводит форму регистрации СИ на основе ЛО и Госреестра """
    """path('measureequipmentreg/<str:str>/', views.MeasureequipmentregView.as_view(), name='measureequipmentreg'),"""
    
    form_class = MeasurEquipmentCreateForm
    template_name = 'equipment/metehereg.html'
    success_url = f'/equipment/measureequipment/{str}'

    def get_object(self, queryset=None):
        return get_object_or_404(Equipment, exnumber=self.kwargs['str'])

    def get_context_data(self, **kwargs):
        context = super(MeasureequipmentregView, self).get_context_data(**kwargs)
        context['title'] = 'Зарегистрировать СИ'
        context['dop'] = Equipment.objects.get(exnumber=self.kwargs['str'])
        return context

    def form_valid(self, form):
        user = self.request.user
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=self.kwargs['str'])
                order.save()
                return redirect(f'/equipment/measureequipment/{self.kwargs["str"]}')
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/measureequipment/{self.kwargs["str"]}')


@login_required
def MEUpdateView(request, str):
    """выводит форму для обновления данных о СИ"""
    """path('meupdate/<str:str>/', views.MEUpdateView, name='meupdate'),"""
    instance=MeasurEquipment.objects.get(pk=str)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = MEUpdateForm(request.POST, instance=MeasurEquipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect(reverse('measureequipment', kwargs={'str': instance.equipment.exnumber}))
        else:
            form = MEUpdateForm(instance=MeasurEquipment.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect(reverse('measureequipment', kwargs={'str': instance.equipment.exnumber}))


class TestingequipmentregView(LoginRequiredMixin, CreateView):
    """ выводит форму регистрации ИО на основе ЛО и характеристик ИО """
    form_class = TestingEquipmentCreateForm
    template_name = 'equipment/metehereg.html'
    success_url = f'/equipment/testequipmentreg/{str}'

    def get_object(self, queryset=None):
        return get_object_or_404(Equipment, exnumber=self.kwargs['str'])

    def get_context_data(self, **kwargs):
        context = super(TestingequipmentregView, self).get_context_data(**kwargs)
        context['title'] = 'Зарегистрировать ИО'
        context['dop'] = Equipment.objects.get(exnumber=self.kwargs['str'])
        return context

    def form_valid(self, form):
        user = self.request.user
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=self.kwargs['str'])
                order.save()
                return redirect(f'/equipment/testequipment/{self.kwargs["str"]}')


@login_required
def TEUpdateView(request, str):
    """выводит форму для обновления данных о ИО"""
    """path('teupdate/<str:str>/', views.TEUpdateView, name='teupdate'),"""
    instance = TestingEquipment.objects.get(pk=str)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = TEUpdateForm(request.POST, instance=TestingEquipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect(reverse('testequipment', kwargs={'str': instance.equipment.exnumber}))
        else:
            form = TEUpdateForm(instance=TestingEquipment.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect(reverse('testequipment', kwargs={'str': instance.equipment.exnumber}))


class HelpingequipmentregView(LoginRequiredMixin, CreateView):
    """ выводит форму регистрации ВО на основе ЛО и характеристик ВО """
    form_class = HelpingEquipmentCreateForm
    template_name = 'equipment/metehereg.html'
    success_url = f'/equipment/helpequipmentreg/{str}'

    def get_object(self, queryset=None):
        return get_object_or_404(Equipment, exnumber=self.kwargs['str'])

    def get_context_data(self, **kwargs):
        context = super(HelpingequipmentregView, self).get_context_data(**kwargs)
        context['title'] = 'Зарегистрировать ВО'
        context['dop'] = Equipment.objects.get(exnumber=self.kwargs['str'])
        return context

    def form_valid(self, form):
        user = self.request.user
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=self.kwargs['str'])
                order.save()
                return redirect(f'/equipment/helpequipment/{self.kwargs["str"]}')


@login_required
def HEUpdateView(request, str):
    """выводит форму для обновления данных о ВО"""
    """path('heupdate/<str:str>/', views.HEUpdateView, name='heupdate'),"""
    instance=HelpingEquipment.objects.get(pk=str)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = HEUpdateForm(request.POST, instance=HelpingEquipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect(reverse('helpequipment', kwargs={'str': instance.equipment.exnumber}))
        else:
            form = HEUpdateForm(instance=HelpingEquipment.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect(reverse('helpequipment', kwargs={'str': instance.equipment.exnumber}))



@login_required
def EquipmentUpdate(request, str):
    """выводит форму для обновления разрешенных полей оборудования ответственному за оборудование и продвинутому пользователю"""
    """path('equipmentind/<str:str>/individuality/', views.EquipmentUpdate, name='equipmentind'),"""
    
    title = Equipment.objects.get(exnumber=str)
    try:
        get_pk = title.personchange_set.latest('pk').pk
        person = Personchange.objects.get(pk=get_pk).person
    except:
        person = 1
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser or request.user == person:
        if request.method == "POST":
            form = EquipmentUpdateForm(request.POST,  instance=Equipment.objects.get(exnumber=str))
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                if title.kategory == 'СИ':
                    try:
                        title.measurequipment
                        return redirect(reverse('measureequipment', kwargs={'str': str}))
                    except:
                        return redirect('euipmentall')
                if title.kategory == 'ИО':
                    try:
                        title.testingequipment
                        return redirect(reverse('testequipment', kwargs={'str': str}))
                    except:
                        return redirect('euipmentall')
                if title.kategory == 'ВО':
                    try:
                        title.helpingequipment
                        return redirect(reverse('helpequipment', kwargs={'str': str}))
                    except:
                        return redirect('euipmentall')
                
        else:
            form = EquipmentUpdateForm(request.POST, instance=Equipment.objects.get(exnumber=str))
        data = {'form': EquipmentUpdateForm(instance=Equipment.objects.get(exnumber=str)), 'title': title
                }
        return render(request, 'equipment/equipment_red.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser or not request.user == person:
        messages.success(request, f' Для внесения записей о приборе нажмите на кнопку'
                                  f' "Внести запись о приборе и смотреть записи (для всех пользователей)"'
                                  f'. Добавить особенности работы или поменять статус может только ответственный '
                                  f'за прибор или у.')
        return redirect('euipmentall')
                



# блок 7 - все поисковики

class VerificatorSearchResultView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    """ выводит результаты поиска по списку поверителей организаций """
    """path('verificatorssearres/', views.VerificatorSearchResultView.as_view(), name='verificatorssearres'),"""

    template_name = URL + '/verificators_list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(VerificatorSearchResultView, self).get_context_data(**kwargs)
        context['serform'] = Searchtestingform  
        return context

    def get_queryset(self):
        name = self.request.GET['name']
        queryset = Verificators.objects.filter(companyName__iregex=name)
        return queryset


class ManufacturerSearchResultView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    """ выводит результаты поиска по списку производителей """
    """path('manufacturersearres/', views.ManufacturerSearchResultView.as_view(), name='manufacturersearres'),"""

    template_name = URL + '/manufacturer_list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(ManufacturerSearchResultView, self).get_context_data(**kwargs)
        context['serform'] = Searchtestingform  
        context['POINTER'] = self.request.user.profile.userid
        return context

    def get_queryset(self):
        name = self.request.GET['name']
        queryset = Manufacturer.objects.filter(companyName__iregex=name)
        return queryset


class SearchResultEquipmentView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку оборудования """
    """path('equipmentallsearres/', views.SearchResultEquipmentView.as_view(), name='equipmentallsearres'),"""
    
    template_name = URL + '/EquipmentLIST.html'

    def get_context_data(self, **kwargs):
        context = super(SearchResultEquipmentView, self).get_context_data(**kwargs)
        lot = self.request.GET['lot']
        exnumber = self.request.GET['exnumber']

        if lot and not exnumber:
            objects = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(lot__iregex=lot)
            context['objects'] = objects
        if exnumber and not lot:
            objects = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(exnumber__iregex=exnumber)
            context['objects'] = objects
        if exnumber and lot:
            objects = Equipment.objects.filter(pointer=self.request.user.profile.userid).filter(exnumber__iregex=exnumber).filter(lot__iregex=lot)
            context['objects'] = objects
        if not exnumber and not lot:
            objects = Equipment.objects.filter(pointer=self.request.user.profile.userid)
            context['objects'] = objects
            
        context['form'] = SearchEqForm(initial={'lot': lot, 'exnumber': exnumber})
        return context





class ReestrsearresView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку госреестров """
    template_name = URL + '/MEcharacterslist.html'

    def get_context_data(self, **kwargs):
        context = super(ReestrsearresView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        reestr = self.request.GET['reestr']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        reestr = self.request.GET['reestr']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if name and not reestr:
            objects = MeasurEquipmentCharakters.objects.\
            filter(Q(name__icontains=name)|Q(name__icontains=name1)).order_by('name')
            context['objects'] = objects
        if reestr and not name:
            objects = MeasurEquipmentCharakters.objects.filter(reestr__icontains=reestr)
            context['objects'] = objects
        if reestr and  name:
            objects = MeasurEquipmentCharakters.objects.filter(reestr__icontains=reestr).\
                filter(Q(name__icontains=name)|Q(name__icontains=name1)).order_by('name')
            context['objects'] = objects
        context['form'] = Searchreestrform(initial={'name': name, 'reestr': reestr})
        context['URL'] = URL
        context['title'] = 'Госреестры, типы, модификации средств измерений'
        return context


class TEcharacterssearresView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку характеристик ИО """
    template_name = URL + '/TEcharacterslist.html'

    def get_context_data(self, **kwargs):
        context = super(TEcharacterssearresView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if name:
            objects = TestingEquipmentCharakters.objects.\
            filter(Q(name__icontains=name)|Q(name__icontains=name1)).order_by('name')
            context['objects'] = objects
        context['form'] = Searchtestingform(initial={'name': name})
        context['URL'] = URL
        context['title'] = 'Характеристики, типы, испытательного оборудования'
        return context


class HEcharacterssearresView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку характеристик ВО """
    template_name = URL + '/HEcharacterslist.html'

    def get_context_data(self, **kwargs):
        context = super(HEcharacterssearresView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if name:
            objects = HelpingEquipmentCharakters.objects.\
            filter(Q(name__icontains=name)|Q(name__icontains=name1)).order_by('name')
            context['objects'] = objects
        context['form'] = Searchtestingform(initial={'name': name})
        context['URL'] = URL
        context['title'] = 'Характеристики, типы, вспомогательного оборудования'
        return context


class SearchResultMeasurEquipmentView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку средств измерений """
    """path('measureequipmentallsearres/', views.SearchResultMeasurEquipmentView.as_view(), name='measureequipmentallsearres'),"""
    
    template_name = URL + '/MEequipmentLIST.html'

    def get_context_data(self, **kwargs):
        context = super(SearchResultMeasurEquipmentView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        exnumber = self.request.GET['exnumber']
        lot = self.request.GET['lot']

        get_id_actual = Verificationequipment.objects.select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        list_ = list(get_id_actual)
        set = []
        for n in list_:
            set.append(n.get('id_actual'))
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        if name and not lot and not exnumber:
            objects = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).\
            filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).order_by('charakters__name')
            context['objects'] = objects
        if lot and not name  and not exnumber:
            objects = MeasurEquipment.objects.filter(equipment__lot=lot).filter(pointer=self.request.user.profile.userid).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and not lot:
            objects = MeasurEquipment.objects.filter(equipment__exnumber__startswith=exnumber).filter(pointer=self.request.user.profile.userid).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and lot:
            objects = MeasurEquipment.objects.filter(equipment__exnumber__startswith=exnumber).filter(pointer=self.request.user.profile.userid).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and not lot:
            objects = MeasurEquipment.objects.filter(equipment__exnumber__startswith=exnumber).filter(pointer=self.request.user.profile.userid).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and lot:
            objects = MeasurEquipment.objects.filter(equipment__exnumber__startswith=exnumber).filter(pointer=self.request.user.profile.userid).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if lot and name and not exnumber:
            objects = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        context['form'] = SearchMEForm(initial={'name': name, 'lot': lot, 'exnumber': exnumber})
        context['URL'] = URL
        return context


class SearchResultTestingEquipmentView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку испытательного оборудования """ 
    """path('testingequipmentallsearres/', views.SearchResultTestingEquipmentView.as_view(), name='testingequipmentallsearres'),"""
    
    template_name = URL + '/TEequipmentLIST.html'

    def get_context_data(self, **kwargs):
        context = super(SearchResultTestingEquipmentView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        exnumber = self.request.GET['exnumber']
        lot = self.request.GET['lot']
        get_id_actual = TestingEquipment.objects.select_related('equipmentSM_att').values('equipmentSM_att'). \
            annotate(id_actual=Max('id')).values('id_actual')
        list_ = list(get_id_actual)
        set = []
        for n in list_:
            set.append(n.get('id_actual'))

        if name and not lot and not exnumber:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).\
            filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                order_by('charakters__name')
            context['objects'] = objects
        if lot and not name  and not exnumber:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and not lot:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and lot:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and not lot:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and lot:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if lot and name and not exnumber:
            objects = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        context['form'] = SearchMEForm(initial={'name': name, 'lot': lot, 'exnumber': exnumber})
        context['URL'] = URL
        return context


class SearchResultHelpingEquipmentView(LoginRequiredMixin, TemplateView):
    """ выводит результаты поиска по списку вспомогательного оборудования """ 
    """path('helpingequipmentallsearres/', views.SearchResultHelpingEquipmentView.as_view(), name='helpingequipmentallsearres'),"""
    
    template_name = URL + '/HEequipmentLIST.html'

    def get_context_data(self, **kwargs):
        context = super(SearchResultHelpingEquipmentView, self).get_context_data(**kwargs)
        name = self.request.GET['name']
        if self.request.GET['name']:
            name1 = self.request.GET['name'][0].upper() + self.request.GET['name'][1:]
        exnumber = self.request.GET['exnumber']
        lot = self.request.GET['lot']

        if name and not lot and not exnumber:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).\
            filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                order_by('charakters__name')
            context['objects'] = objects
        if lot and not name  and not exnumber:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and not lot:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and lot:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if exnumber and name and not lot:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                order_by('charakters__name')
            context['objects'] = objects
        if exnumber and not name and lot:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber=exnumber).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        if lot and name and not exnumber:
            objects = HelpingEquipment.objects.filter(pointer=self.request.user.profile.userid).\
                filter(Q(charakters__name__icontains=name)|Q(charakters__name__icontains=name1)).\
                filter(equipment__lot=lot).order_by('charakters__name')
            context['objects'] = objects
        context['form'] = SearchMEForm(initial={'name': name, 'lot': lot, 'exnumber': exnumber})
        context['URL'] = URL
        return context



# блок 8  принадлежности к оборудованию

class DocsConsView(View, SuccessMessageMixin):
    """ выводит список принадлежностей прибора и форму для добавления принадлежности """
    """path('docsreg/<str:str>/', views.DocsConsView.as_view(), name='docsreg'),"""
    
    def get(self, request, str):
        template_name = 'equipment/EdocumentsLIST.html'
        form = DocsConsCreateForm()
        title = Equipment.objects.get(exnumber=str)
        objects = DocsCons.objects.filter(equipment__exnumber=str).order_by('pk')
        context = {
                'title': title,
                'form': form,
                'objects': objects,
                }
        return render(request, template_name, context)

    def post(self, request, str, *args, **kwargs):
        form = DocsConsCreateForm(request.POST)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipment = Equipment.objects.get(exnumber=str)
                order.save()
                return redirect(f'/equipment/docsreg/{str}')
        else:
            messages.add_message(request, messages.SUCCESS, 'Раздел доступен только продвинутому пользователю')
            return redirect(f'/equipment/docsreg/{str}')



# блок 9 - внесение и обновление поверка и аттестация

@login_required
def VerificationReg(request, str):
    """выводит форму для внесения сведений о поверке"""
    """equipment/MEverificationreg.html"""
    
    title = Equipment.objects.get(exnumber=str)
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            form = VerificationRegForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.equipmentSM = MeasurEquipment.objects.get(equipment__exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect(reverse('measureequipmentver', kwargs={'str': str}))
    else:
        form = VerificationRegForm()
    data = {
        'form': form,
        'title': title
    }
    return render(request, 'equipment/MEverificationreg.html', data)


@login_required
def VerUpdateView(request, str):
    """выводит форму для обновления сведений о поверке """
    """path('verificationupdate/<str:str>/', views.VerUpdateView, name='verificationupdate'),"""
    
    for_a = Verificationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber
    title = Equipment.objects.get(exnumber=a)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = VerificationRegForm(request.POST, instance= Verificationequipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                find_ver = Verificationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save()  
                return redirect(order)
        else:
            form = VerificationRegForm(instance=Verificationequipment.objects.get(pk=str))
        data = {'form': form,
                'title': title,
               }                
        return render(request, 'equipment/MEverificationreg.html', data)
        
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('verificationupdate')


@login_required
def CalibrationReg(request, str):
    """выводит форму для внесения сведений о калибровке"""
    """path('measureequipment/calibrationreg/<str:str>/', views.CalibrationReg, name='measureequipmentcalibrationreg'),"""
    """equipment/MEcalibrationreg.html"""
    title = Equipment.objects.get(exnumber=str)
    
    if request.method == "POST":
        form = CalibrationRegForm(request.POST, request.FILES)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.equipmentSM = MeasurEquipment.objects.get(equipment__exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect(reverse('measureequipmentcal', kwargs={'str': str}))
    else:
        form = CalibrationRegForm()
    data = {
        'form': form,
        'title': title
    }
    return render(request, 'equipment/MEcalibrationreg.html', data)


@login_required
def CalibrationUpdateView(request, str):
    """выводит форму для обновления сведений о калибровке """
    """path('сalibrationupdate/<str:str>/', views.CalibrationUpdateView, name='сalibrationupdate'),"""

    for_a = Calibrationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber
    title = Equipment.objects.get(exnumber=a)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = CalibrationRegForm(request.POST, instance= Calibrationequipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                find_ver = Calibrationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save()  
                return redirect(order)
        else:
            form = CalibrationRegForm(instance=Calibrationequipment.objects.get(pk=str))
        data = {'form': form,
                'title': title
               }                
        return render(request, 'equipment/MEcalibrationreg.html', data)
        
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('сalibrationupdate')
        

@login_required
def AttestationReg(request, str):
    """выводит форму для внесения сведений об аттестации"""
    """path('testingequipment/attestationreg/<str:str>/', views.AttestationReg, name='testingequipmentattestationreg'),"""
    """equipment/TEattestationreg.html"""

    title = Equipment.objects.get(exnumber=str)
    
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            form = AttestationRegForm(request.POST, request.FILES)
            if form.is_valid():
                order = form.save(commit=False)
                order.equipmentSM = TestingEquipment.objects.get(equipment__exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect(reverse('testingequipmentatt', kwargs={'str': str}))
    else:
        form = AttestationRegForm()
    data = {
        'form': form,
        'title': title
    }
    return render(request, 'equipment/TEattestationreg.html', data)


@login_required
def AttestationUpdateView(request, str):
    """выводит форму для обновления сведений о аттестации """
    """path('attestationupdate/<str:str>/', views.AttestationUpdateView, name='attestationupdate'),"""

    for_a = Attestationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber
    title = Equipment.objects.get(exnumber=a)
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = AttestationRegForm(request.POST, instance= Attestationequipment.objects.get(pk=str))                                                       
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                find_ver = Attestationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save()  
                return redirect(order)
        else:
            form = AttestationRegForm(instance=Attestationequipment.objects.get(pk=str))
        data = {'form': form,
                'title': title
               }                
        return render(request, 'equipment/TEattestationreg.html', data)
        
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect('attestationupdate')
        

@login_required
def EquipmentMetrologyUpdate(request, str):
    """выводит форму для обновления постоянных особенностей поверки"""
    title = Equipment.objects.get(exnumber=str)
    try:
        get_pk = title.personchange_set.latest('pk').pk
        person = Personchange.objects.get(pk=get_pk).person
    except:
        person = 1

    if person == request.user or request.user.is_superuser or request.user.has_perm('equipment.add_equipment'):
        if request.method == "POST":
            form = MetrologyUpdateForm(request.POST, instance=Equipment.objects.get(exnumber=str))
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                if title.kategory == 'СИ':
                    return redirect(reverse('measureequipmentver', kwargs={'str': str}))
                if title.kategory == 'ИО':
                    return redirect(reverse('testingequipmentatt', kwargs={'str': str}))
    if person != request.user or  not request.user.is_superuser or not request.user.has_perm('equipment.add_equipment'):
        messages.success(request, f'. поменять статус может только ответственный за поверку.')
        return redirect(reverse('measureequipmentver', kwargs={'str': str}))
    else:
        form = MetrologyUpdateForm(instance=Equipment.objects.get(exnumber=str))
    data = {'form': form, 'title': title
            }
    return render(request, 'equipment/metrologyindividuality.html', data)


class VerificationequipmentView(LoginRequiredMixin, View):
    """ выводит историю поверок и форму для добавления комментария к истории поверок """
    """path('measureequipment/verification/<str:str>/', views.VerificationequipmentView.as_view(), name='measureequipmentver'),"""
    """'equipment/MEverification.html'"""

    def get(self, request, str):
        note = Verificationequipment.objects.filter(equipmentSM__equipment__exnumber=str).order_by('-pk')
        try:
            strreg = note.latest('pk').equipmentSM.equipment.exnumber
        except:
            strreg = Equipment.objects.get(exnumber=str).exnumber
        try:
            calinterval = note.latest('pk').equipmentSM.charakters.calinterval
        except:
            calinterval = '-'
        title = Equipment.objects.get(exnumber=str)
        try:
            dateorder = Verificationequipment.objects.filter(equipmentSM__equipment__exnumber=str).last().dateorder
        except:
            dateorder = 'не поверен'
        now = date.today()
        try:
            comment = CommentsVerificationequipment.objects.filter(forNote__exnumber=str).last().note
        except:
            comment = ''
        form = CommentsVerificationCreationForm(initial={'comment': comment})
        data = {'note': note,
                'title': title,
                'calinterval': calinterval,
                'now': now,
                'dateorder': dateorder,
                'form': form,
                'comment': comment,
                'strreg': strreg,
                }
        return render(request, 'equipment/MEverification.html', data)

    def post(self, request, str, *args, **kwargs):
        form = CommentsVerificationCreationForm(request.POST)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.author = request.user
                order.forNote = Equipment.objects.get(exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, f'Комментировать может только ответственный за поверку приборов')
            return redirect(reverse('measureequipmentver', kwargs={'str': str}))


class CalibrationequipmentView(LoginRequiredMixin, View):
    """ выводит историю калибровок и форму для добавления комментария к истории калибровок """
    """path('measureequipment/calibration/<str:str>/', views.CalibrationequipmentView.as_view(), name='measureequipmentcal'),"""
    """equipment/MEcalibration.html"""

    def get(self, request, str):
        note = Calibrationequipment.objects.filter(equipmentSM__equipment__exnumber=str).order_by('-pk')
        try:
            strreg = note.latest('pk').equipmentSM.equipment.exnumber
        except:
            strreg = Equipment.objects.get(exnumber=str).exnumber
        try:
            calinterval = note.latest('pk').equipmentSM.charakters.calinterval
        except:
            calinterval = '-'
        title = Equipment.objects.get(exnumber=str)
        try:
            dateorder = Calibrationequipment.objects.filter(equipmentSM__equipment__exnumber=str).last().dateorder
        except:
            dateorder = 'не поверен'
        now = date.today()
        try:
            comment = CommentsVerificationequipment.objects.filter(forNote__exnumber=str).last().note
        except:
            comment = ''
        form = CommentsVerificationCreationForm(initial={'comment': comment})
        data = {'note': note,
                'title': title,
                'calinterval': calinterval,
                'now': now,
                'dateorder': dateorder,
                'form': form,
                'comment': comment,
                'strreg': strreg,
                }
        return render(request, 'equipment/MEcalibration.html', data)

    def post(self, request, str, *args, **kwargs):
        form = CommentsVerificationCreationForm(request.POST)
        if  request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.author = request.user
                order.forNote = Equipment.objects.get(exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, f'Комментировать может только ответственный за поверку приборов')
            return redirect(reverse('measureequipmentcal', kwargs={'str': str}))


class AttestationequipmentView(LoginRequiredMixin, View):
    """ выводит историю аттестаций и форму для добавления комментария к истории аттестаций """
    """path('testingequipment/attestation/<str:str>/', views.AttestationequipmentView.as_view(), name='testingequipmentatt'),"""
    """equipment/TEattestation.html"""

    def get(self, request, str):
        note = Attestationequipment.objects.filter(equipmentSM__equipment__exnumber=str).order_by('-pk')
        try:
            strreg = note.latest('pk').equipmentSM.equipment.exnumber
        except:
            strreg = Equipment.objects.get(exnumber=str).exnumber
        try:
            calinterval = note.latest('pk').equipmentSM.charakters.calinterval
        except:
            calinterval = '-'
        title = Equipment.objects.get(exnumber=str)
        try:
            dateorder = Attestationequipment.objects.filter(equipmentSM__equipment__exnumber=str).last().dateorder
        except:
            dateorder = 'не аттестован'
        now = date.today()
        try:
            comment = CommentsAttestationequipment.objects.filter(forNote__exnumber=str).last().note
        except:
            comment = ''
        form = CommentsAttestationequipmentForm(initial={'comment': comment})
        data = {'note': note,
                'title': title,
                'calinterval': calinterval,
                'now': now,
                'dateorder': dateorder,
                'form': form,
                'comment': comment,
                'strreg': strreg,
                }
        return render(request, 'equipment/TEattestation.html', data)

    def post(self, request, str, *args, **kwargs):
        form = CommentsAttestationequipmentForm(request.POST)
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            if form.is_valid():
                order = form.save(commit=False)
                order.author = request.user
                order.forNote = Equipment.objects.get(exnumber=str)
                order.save()
                return redirect(order)
        else:
            messages.success(request, f'Комментировать может только ответственный за поверку приборов')
            return redirect(reverse('testingequipmentattestation', kwargs={'str': str}))


class HaveorderVerView(LoginRequiredMixin, UpdateView):
    """ выводит форму добавления инфо о заказе поверки """
    template_name = 'equipment/reg.html'
    form_class = OrderMEUdateForm

    def get_object(self, queryset=None):
        queryset_get = Verificationequipment.objects. \
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        q = Verificationequipment.objects.filter(id__in=set). \
            get(equipmentSM_id=self.kwargs['pk'])
        return q

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.save()
            return redirect('/equipment/measureequipmentall/')
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/measureequipmentall/')

    def get_context_data(self, **kwargs):
        context = super(HaveorderVerView, self).get_context_data(**kwargs)
        context['title'] = "Заказана поверка или новое СИ"
        return context


class HaveorderAttView(LoginRequiredMixin, UpdateView):
    """ выводит форму добавления инфо о заказе аттестации """
    template_name = 'equipment/reg.html'
    form_class = OrderMEUdateForm

    def get_object(self, queryset=None):
        queryset_get = Attestationequipment.objects. \
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        q = Attestationequipment.objects.filter(id__in=set). \
            get(equipmentSM_id=self.kwargs['pk'])
        return q

    def form_valid(self, form):
        order = form.save(commit=False)
        user = User.objects.get(username=self.request.user)
        if user.has_perm('equipment.add_equipment') or user.is_superuser:
            order.save()
            return redirect('/equipment/testingequipmentall/')
        else:
            messages.success(self.request, "Раздел доступен только продвинутому пользователю")
            return redirect('/equipment/testingequipmentall/')

    def get_context_data(self, **kwargs):
        context = super(HaveorderAttView, self).get_context_data(**kwargs)
        context['title'] = "Заказана аттестация или новое ИО"
        return context



# блок 10 - индивидуальные страницы СИ ИО ВО 

class StrMeasurEquipmentView(LoginRequiredMixin, View):
    """ выводит отдельную страницу СИ """
    """ path('measureequipment/<str:str>/', views.StrMeasurEquipmentView.as_view(), name='measureequipment'),"""
    """MEequipmentSTR.html"""
    
    def get(self, request, str):
        POINTER = request.user.profile.userid
        note = Verificationequipment.objects.filter(equipmentSM__equipment__exnumber=str).order_by('-pk')
        obj = get_object_or_404(MeasurEquipment, equipment__exnumber=str)
        lookyearform = LookYearForm()
        context = {
            'obj': obj,
            'note': note,
            'POINTER': POINTER,
            'lookyearform': lookyearform,
        }
        return render(request, URL + '/MEequipmentSTR.html', context)


class StrTestEquipmentView(LoginRequiredMixin, View):
    """ выводит отдельную страницу ИО """
    def get(self, request, str):
        POINTER = request.user.profile.userid
        note = Attestationequipment.objects.filter(equipmentSM__equipment__exnumber=str).order_by('-pk')
        obj = get_object_or_404(TestingEquipment, equipment__exnumber=str)
        lookyearform = LookYearForm()
        context = {
            'obj': obj,
            'note': note,
            'POINTER': POINTER,
            'lookyearform': lookyearform,
        }
        return render(request, URL + '/TEequipmentSTR.html', context)


class StrHelpEquipmentView(LoginRequiredMixin, View):
    """ выводит отдельную страницу ВО """
    def get(self, request, str):
        POINTER = request.user.profile.userid
        obj = get_object_or_404(HelpingEquipment, equipment__exnumber=str)
        lookyearform = LookYearForm()
        context = {
            'obj': obj,
            'POINTER': POINTER,
            'lookyearform': lookyearform,
        }
        return render(request, URL + '/HEequipmentSTR.html', context)


# блок 11 - все комментарии ко всему

class CommentsView(View):
    """ выводит комментарии к оборудованию и форму для добавления комментариев (записи в карточке прибора для пользователей всех уровней) """
    """ path('equipmentcomments/<str:str>', views.CommentsView.as_view(), name='equipmentcomments'),"""
    
    form_class = NoteCreationForm
    initial = {'key': 'value'}
    template_name = 'equipment/comments.html'

    def get(self, request, str):
        note = CommentsEquipment.objects.filter(forNote__exnumber=str).order_by('-pk')
        title = Equipment.objects.get(exnumber=str)
        form = NoteCreationForm()
        return render(request, 'equipment/Ecomments.html', {'note': note, 'title': title, 'form': form, 'URL': URL})

    def post(self, request, str, *args, **kwargs):
        form = NoteCreationForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.forNote = Equipment.objects.get(exnumber=str)
            order.save()
            messages.success(request, f'Запись добавлена!')
            return redirect(reverse('equipmentcomments', kwargs={'str': str}))
        else:
            messages.success(request, f'что-то пошло не так')
            return redirect(reverse('equipmentcomments', kwargs={'str': str}))
            



# блок 12 - вывод списков и форм  для метрологического обеспечения

class SearchMustVerView(LoginRequiredMixin, ListView):
    """ выводит список СИ у которых дата заказа поверки совпадает с указанной либо раньше неё"""
    """path('measureequipmentall/mustver/', views.SearchMustVerView.as_view(), name='mustver'),"""

    template_name = URL + '/MEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']

    def get_context_data(self, **kwargs):
        context = super(SearchMustVerView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset_get = Verificationequipment.objects.filter(haveorder=False).\
            filter(pointer=self.request.user.profile.userid).\
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        queryset_get1 = Verificationequipment.objects.filter(id__in=set).\
            filter(dateorder__lte=serdate).values('equipmentSM__id')
        b = list(queryset_get1)
        set1 = []
        for i in b:
            a = i.get('equipmentSM__id')
            set1.append(a)
        queryset = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(id__in=set1).filter(equipment__status='Э')
        return queryset


class SearchMustAttView(LoginRequiredMixin, ListView):
    """ выводит список ИО у которых дата заказа аттестации совпадает с указанной либо раньше неё"""

    template_name = URL + '/TEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']

    def get_context_data(self, **kwargs):
        context = super(SearchMustAttView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset_get = Attestationequipment.objects.filter(haveorder=False).\
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        queryset_get1 = Attestationequipment.objects.filter(id__in=set).\
            filter(dateorder__lte=serdate).values('equipmentSM__id')
        b = list(queryset_get1)
        set1 = []
        for i in b:
            a = i.get('equipmentSM__id')
            set1.append(a)
        queryset = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(id__in=set1).filter(equipment__status='Э')
        return queryset


class SearchNotVerView(LoginRequiredMixin, ListView):
    """ выводит список СИ у которых дата окончания поверки совпадает с указанной либо раньше неё"""

    template_name = URL + '/MEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']

    def get_context_data(self, **kwargs):
        context = super(SearchNotVerView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset_get = Verificationequipment.objects.\
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        queryset_get1 = Verificationequipment.objects.filter(id__in=set).\
            filter(datedead__lte=serdate).values('equipmentSM__id')
        b = list(queryset_get1)
        set1 = []
        for i in b:
            a = i.get('equipmentSM__id')
            set1.append(a)
        queryset = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(id__in=set1).exclude(equipment__status='C')
        return queryset


class SearchNotAttView(LoginRequiredMixin, ListView):
    """ выводит список ИО у которых дата окончания аттестации совпадает с указанной либо раньше неё"""

    template_name = URL + '/TEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']

    def get_context_data(self, **kwargs):
        context = super(SearchNotAttView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset_get = Attestationequipment.objects.\
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        queryset_get1 = Attestationequipment.objects.filter(id__in=set).\
            filter(datedead__lte=serdate).values('equipmentSM__id')
        b = list(queryset_get1)
        set1 = []
        for i in b:
            a = i.get('equipmentSM__id')
            set1.append(a)
        queryset = TestingEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(id__in=set1).exclude(equipment__status='C')
        return queryset
           
# .filter()[Total-10:Total]

class SearchMustOrderView(LoginRequiredMixin, ListView):
    """ выводит список СИ у которых месяц заказа новых совпадает с указанным либо раньше него"""

    template_name = URL + '/MEequipmentLIST.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']

    def get_context_data(self, **kwargs):
        context = super(SearchMustOrderView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SearchMEForm()
        return context

    def get_queryset(self):
        serdate = self.request.GET['date']
        queryset_get = Verificationequipment.objects.filter(haveorder=False).\
            select_related('equipmentSM').values('equipmentSM'). \
            annotate(id_actual=Max('id')).values('id_actual')
        b = list(queryset_get)
        set = []
        for i in b:
            a = i.get('id_actual')
            set.append(a)
        queryset_get1 = Verificationequipment.objects.filter(id__in=set).\
            filter(dateordernew__lte=serdate).values('equipmentSM__id')
        b = list(queryset_get1)
        set1 = []
        for i in b:
            a = i.get('equipmentSM__id')
            set1.append(a)
        queryset = MeasurEquipment.objects.filter(pointer=self.request.user.profile.userid).filter(id__in=set1).filter(equipment__status='Э')
        return queryset


class VerificationLabelsView(LoginRequiredMixin, TemplateView):
    """выводит форму для ввода внутренних номеров для распечатки этикеток о метрологическом обслуживании приборов """
    template_name = URL + '/labels.html'

    def get_context_data(self, **kwargs):
        context = super(VerificationLabelsView, self).get_context_data(**kwargs)
        context['form'] = LabelEquipmentform()
        return context



# блок 13 - ТОиР

@login_required
def ServiceEquipmentregMEView(request, str):
    """выводит форму для добавления постоянного ТОИР к СИ"""
    """path('toreg/<str:str>/', views.ServiceEquipmentregMEView, name='toreg'),"""
    
    charakters = MeasurEquipmentCharakters.objects.get(pk=str) 
    etype = 1
    for_title = f'{charakters.reestr}, {charakters.name},'
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            try: 
                ServiceEquipmentME.objects.get(charakters=charakters)
                form = ServiceEquipmentregForm(request.POST, instance=ServiceEquipmentME.objects.get(charakters=charakters))  
            except:
                form = ServiceEquipmentregForm(request.POST)  
            if form.is_valid():
                order = form.save(commit=False)
                order.pointer = request.user.profile.userid
                order.charakters = charakters
                order.save()
                return redirect('measurequipmentcharacterslist')
            else:
                messages.success(request, 'Раздел доступен только продвинутому пользователю')
                return redirect('measurequipmentcharacterslist')
    else:
        try: 
            ServiceEquipmentME.objects.get(charakters=charakters)
            form = ServiceEquipmentregForm(instance=ServiceEquipmentME.objects.get(charakters=charakters))
        except:
            form = ServiceEquipmentregForm()
        data = {'form': form,
                'etype': etype, 
                'for_title': for_title,
               }                
        return render(request, 'equipment/toreg.html', data)



@login_required
def ServiceEquipmentregTEView(request, str):
    """выводит форму для добавления постоянного ТОИР к ИО"""
    """path('toregte/<str:str>/', views.ServiceEquipmentregTEView, name='toregte'),"""
    
    charakters = TestingEquipmentCharakters.objects.get(pk=str) 
    etype = 2
    for_title = charakters.name
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            try: 
                ServiceEquipmentTE.objects.get(charakters=charakters)
                form = ServiceEquipmentregTEForm(request.POST, instance=ServiceEquipmentTE.objects.get(charakters=charakters))  
            except:
                form = ServiceEquipmentregTEForm(request.POST)  
            if form.is_valid():
                order = form.save(commit=False)
                order.pointer = request.user.profile.userid
                order.charakters = charakters
                order.save()
                return redirect('testingequipmentcharacterslist')
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect('testingequipmentcharacterslist')
    else:
        try: 
            ServiceEquipmentTE.objects.get(charakters=charakters)
            form = ServiceEquipmentregTEForm(instance=ServiceEquipmentTE.objects.get(charakters=charakters))
        except:
            form = ServiceEquipmentregTEForm()
        data = {'form': form, 
                'etype': etype,
                'for_title': for_title,
               }                
        return render(request, 'equipment/toreg.html', data)



@login_required
def ServiceEquipmentregHEView(request, str):
    """выводит форму для добавления постоянного ТОИР к ВО"""
    """path('toreghe/<str:str>/', views.ServiceEquipmentregHEView, name='toreghe'),"""

    charakters = HelpingEquipmentCharakters.objects.get(pk=str) 
    etype = 3
    for_title = charakters.name
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            try:  
                ServiceEquipmentHE.objects.get(charakters=charakters)
                form = ServiceEquipmentregHEForm(request.POST, instance=ServiceEquipmentHE.objects.get(charakters=charakters))  
            except:
                form = ServiceEquipmentregHEForm(request.POST)  
            if form.is_valid():
                order = form.save(commit=False)
                order.pointer = request.user.profile.userid
                order.charakters = charakters
                order.save()
                return redirect('helpingequipmentcharacterslist')
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect('helpingequipmentcharacterslist')
    else:
        try: 
            ServiceEquipmentHE.objects.get(charakters=charakters)
            form = ServiceEquipmentregHEForm(instance=ServiceEquipmentHE.objects.get(charakters=charakters))
        except:
            form = ServiceEquipmentregHEForm()
        data = {'form': form, 
                'etype': etype,
                'for_title': for_title,
               }                
        return render(request, 'equipment/toreg.html', data)


class ServiceView(LoginRequiredMixin, ListView):
    """Выводит главную страницу просмотра и планирования ТОиР"""
    """ path('service/', views.ServiceView.as_view(), name='service'), """
    
    template_name = URL + '/service.html'
    context_object_name = 'objects'
    ordering = ['charakters_name']
    paginate_by = 12

    def get_queryset(self):
        queryset = ServiceEquipmentU.objects.filter(pointer=self.request.user.profile.userid).filter(year=str(now.year))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ServiceView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['form'] = SimpleSearchForm()
        context['year'] = now.year
        context['createyearform'] = CreateYearForm()
        context['getyearform'] = GetYearForm()
        context['lookyearform'] = LookYearForm()
        return context


@login_required
def ServiceEquipmentUUpdateView(request, str):
    """выводит форму для обновления данных о ТО-2 план"""
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        if request.method == "POST":
            form = ServiceEquipmentUUpdateForm(request.POST, instance=ServiceEquipmentU.objects.get(pk=str))                                                    
            if form.is_valid():
                order = form.save(commit=False)
                order.save()
                return redirect(reverse('serviceplan', kwargs={'str': str}))
        else:
            form = ServiceEquipmentUUpdateForm(instance=ServiceEquipmentU.objects.get(pk=str))
        data = {'form': form,
                }
        return render(request, 'equipment/reg.html', data)
    if not request.user.has_perm('equipment.add_equipment') or not request.user.is_superuser:
        messages.success(request, 'Раздел доступен только продвинутому пользователю')
        return redirect(reverse('serviceplan', kwargs={'str': str}))



@login_required
def ServiceEquipmentUFactUpdateView(request, str):
    """выводит форму для обновления данных о ТО-2 факт"""
    if request.method == "POST":
        form = ServiceEquipmentUFactUpdateViewForm(request.POST, instance=ServiceEquipmentUFact.objects.get(pk_pointer=str))                                                    
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            return redirect(reverse('serviceplan', kwargs={'str': str}))
    else:
        form = ServiceEquipmentUFactUpdateViewForm(instance=ServiceEquipmentUFact.objects.get(pk_pointer=str))
        data = {'form': form,
                }
        return render(request, 'equipment/reg.html', data)



class ServiceSearchResultView(LoginRequiredMixin, ListView):
    """ выводит результаты поиска по списку ТО-2 по номеру оборудования """
    """ path('serviceyearsearchresult/', views.ServiceSearchResultView.as_view(), name='serviceyearsearchresult'),"""

    template_name = URL + '/serviceyear.html'
    context_object_name = 'objects' 

    def get_context_data(self, **kwargs):
        context = super(ServiceSearchResultView, self).get_context_data(**kwargs)
        context['URL'] = URL
        context['year'] = self.request.GET.get('qwery1')
        context['form'] = DubleSearchForm()
        return context

    def get_queryset(self):
        qwery = self.request.GET.get('qwery')
        year = self.request.GET.get('qwery1')
        queryset = ServiceEquipmentU.objects.filter(pointer=self.request.user.profile.userid).filter(equipment__exnumber__startswith=qwery).filter(year=year)
        return queryset


@login_required
def ServiceCreateView(request):
    """формирует график ТОИР на указанный год """   
    """страницу не выводит, только действие  """ 
    
    if request.method == 'GET':
        year = request.GET.get('date')
        queryset = Equipment.objects.filter(pointer=request.user.profile.userid).filter(yearintoservice__lte=year).filter(serviceneed=True)
        if len(list(ServiceEquipmentU.objects.filter(pointer=request.user.profile.userid).filter(year=year))) !=0:        
            messages.success(request, f'График ТОиР на {year} год уже был сформирован ранее, добавить в график новый прибор можно через блок ТОиР на индивидуальной странице прибора')
            return redirect('service')
        else:
            for i in queryset:
                ServiceEquipmentU.objects.get_or_create(equipment=i, year=year)
            messages.success(request, f'График ТОиР на {year} год успешно сформирован')
            return redirect('service')


class ToMEView(LoginRequiredMixin, View):
    """выводит описание ТО для СИ """
    template_name = URL + '/to.html'

    def get(self, request, str):
        obj = ServiceEquipmentME.objects.get(pk=str)
        return render(request, URL + '/to.html', {'obj': obj,})


class ToTEView(LoginRequiredMixin, View):
    """выводит описание ТО для ИО """
    template_name = URL + '/to.html'

    def get(self, request, str):
        obj = ServiceEquipmentTE.objects.get(pk=str)
        return render(request, URL + '/to.html', {'obj': obj,})

class ToHEView(LoginRequiredMixin, View):
    """выводит описание ТО для ВО """
    template_name = URL + '/to.html'

    def get(self, request, str):
        obj = ServiceEquipmentHE.objects.get(pk=str)
        return render(request, URL + '/to.html', {'obj': obj,})


class ServiceCreateIndividualView(TemplateView):
    """выводит форму для добавления или удаления единицы оборудования из графика ТОиР на указанный год """
    """path('itemserviceupdate/<str:str>/', views.ServiceCreateIndividualView.as_view(), name='itemserviceupdate'),"""
    template_name = URL + '/itemservise.html'

    def get_context_data(self, str, **kwargs):
        context = super(ServiceCreateIndividualView, self).get_context_data(**kwargs)
        context['obj'] = Equipment.objects.get(pk=str)
        context['addform'] = AddYearForm()
        context['delform'] = DelYearForm()
        return context


@login_required
def AddserviceitemView(request, str):
    """добавляет единицу оборудования в график ТОиР на указанный год """
    
    
    if request.method == 'GET':
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            year = request.GET.get('date')
            i = Equipment.objects.get(pk=str)
            ServiceEquipmentU.objects.get_or_create(equipment=i, year=year)
            messages.success(request, 'Прибор успешно добавлен в график ТОиР')
            return redirect(f'/equipment/itemserviceupdate/{str}/')
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect(f'/equipment/itemserviceupdate/{str}/')
            


@login_required
def DelserviceitemView(request, str):
    """удаляет единицу оборудования из график ТОиР на указанный год """
    if request.method == 'GET':
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            year = request.GET.get('date')
            i = Equipment.objects.get(pk=str)
            ServiceEquipmentU.objects.get(equipment=i, year=year).delete()
            messages.success(request, 'Прибор успешно удален из графика ТОиР')
            return redirect(f'/equipment/itemserviceupdate/{str}/')
        else:
            messages.success(request, 'Раздел доступен только продвинутому пользователю')
            return redirect(f'/equipment/itemserviceupdate/{str}/')
        

class ServiceYearView(LoginRequiredMixin, View):
    """вывод страницы - ТОИР за год, год передан в форме поиска на предыдущей странице"""
    """ path('serviceyear/', views.ServiceYearView.as_view(), name='serviceyear'),"""
    
    def get(self, request):
        date = self.request.GET['date']
        objects = ServiceEquipmentU.objects.filter(pointer=self.request.user.profile.userid).filter(year=date)
        form =  DubleSearchForm()
        URL = 'equipment'
        year= date
        yearform = YearForm()
        context = {
            'objects': objects,
            'URL': URL,
            'form': form,
            'yearform': yearform,
            'year': year,
        }
        template_name = 'equipment/serviceyear.html'
        return render(request, template_name, context)
        

@login_required
def ServiceStrView(request,  str):
    """ выводит отдельную страницу плана ТО2 """
    """path('serviceplan/<str:str>/', views.ServiceStrView, name='serviceplan'),"""
    """URL + '/serviceplan.html'"""
    
    try:
        a = request.GET.get('equipment_pk')
        b = request.GET.get('date')
        if a and b:
            obj = get_object_or_404(ServiceEquipmentU, equipment__pk=a, year=b)
            pk_pointer = obj.pk
            obj2 = get_object_or_404(ServiceEquipmentUFact, pk_pointer=pk_pointer)      
        else:
            obj = get_object_or_404(ServiceEquipmentU, pk=str)
            obj2 = get_object_or_404(ServiceEquipmentUFact, pk_pointer=str)
        year=obj.year
        context = {
        'obj': obj, 'obj2': obj2, 
            'year': year,
            'a': a,
            'b': b,
                }
        return render(request, URL + '/serviceplan.html', context)
    except:
        messages.success(request, 'Этого прибора в графике ТОиР на указанный год нет')
        return redirect('managerequipment')
    


# блок 14 - все кнопки удаления объектов

@login_required
def EquipmentDeleteView(request, str):
    """для кнопки удаления ЛО"""
    """не выводит страницу, выполняет действие"""
    """path('equipmentdelete/<str:str>/', views.EquipmentDeleteView, name='equipmentdelete'),"""
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Equipment.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Оборудование удалено!')
            return redirect('euipmentall')            
        except:
            messages.success(request, 'Оборудование невозможно удалить')
            return redirect('equipmentlist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('equipmentlist')


@login_required
def VeragreementDeleteView(request, str):
    """для кнопки удаления договора с поверителем"""
    """не выводит страницу, выполняет действие"""
    """path('veragreementdelete/<str:str>/', views.VeragreementDeleteView, name='veragreementdelete'),"""
    ruser=request.user.profile.userid
    a = Agreementverification.objects.filter(pointer=ruser).count()
    if ((request.user.has_perm('equipment.add_equipment') or request.user.is_superuser) and a >= 1):
        try:
            ruser=request.user.profile.userid
            note = Agreementverification.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Договор удален!')
            return redirect('agreementcompanylist')            
        except:
            messages.success(request, 'Невозможно удалить')
            return redirect('agreementcompanylist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('agreementcompanylist')


@login_required
def VerificatorDeleteView(request, str):
    """для кнопки удаления поверителя"""
    """не выводит страницу, выполняет действие"""
    """path('veragrificatordelete/<str:str>/', views.VerificatorDeleteView, name='veragrificatordelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Verificators.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Поверитель удален!')
            return redirect('verificatorsreg')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлен договор или запись о поверке с этим поверителем')
            return redirect('verificatorsreg')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('verificatorsreg')


@login_required
def ManufacturerDeleteView(request, str):
    """для кнопки удаления производителя"""
    """не выводит страницу, выполняет действие"""
    """path('manufacturerdelete/<str:str>/', views.ManufacturerDeleteView, name='manufacturerdelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Manufacturer.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Производитель удален!')
            return redirect('manufacturerlist')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлен прибор с этим поверителем')
            return redirect('manufacturerlist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('manufacturerlist')


@login_required
def MecharaktersDeleteView(request, str):
    """для кнопки удаления характеристик СИ (госреестра)"""
    """не выводит страницу, выполняет действие"""
    """path('mecharaktersdelete/<str:str>/', views.MecharaktersDeleteView, name='mecharaktersdelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = MeasurEquipmentCharakters.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Характеристики СИ (Госреестр) удален!')
            return redirect('measurequipmentcharacterslist')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлено средство измерения с этими характеристиками')
            return redirect('measurequipmentcharacterslist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('measurequipmentcharacterslist')


@login_required
def HecharaktersDeleteView(request, str):
    """для кнопки удаления характеристик ВО """
    """не выводит страницу, выполняет действие"""
    """path('hecharaktersdelete/<str:str>/', views.HecharaktersDeleteView, name='hecharaktersdelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = HelpingEquipmentCharakters.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Характеристики вспомогательного оборудования  удалены!')
            return redirect('helpingequipmentcharacterslist')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлено вспомогательное оборудование с этими характеристиками')
            return redirect('helpingequipmentcharacterslist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('helpingequipmentcharacterslist')


@login_required
def TecharaktersDeleteView(request, str):
    """для кнопки удаления характеристик ИО """
    """не выводит страницу, выполняет действие"""
    """path('techaraktersdelete/<str:str>/', views.TecharaktersDeleteView, name='techaraktersdelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = TestingEquipmentCharakters.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Характеристики испытательного оборудования  удалены!')
            return redirect('testingequipmentcharacterslist')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлено испытательного оборудование с этими характеристиками')
            return redirect('testingequipmentcharacterslist')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('testingequipmentcharacterslist')


@login_required
def EquipmentKategoryUpdate(request, str):
    """выводит форму смены категории оборудования и удаления соответствующего СИ/ИО/ВО """
    """path('equipmentkategoryupdate/<str:str>/', views.EquipmentKategoryUpdate, name='equipmentkategoryupdate'),"""
    ruser=request.user.profile.userid   
    instance_equipment = Equipment.objects.filter(pointer=ruser).get(pk=str)
    try:
        instance_equipment.measurequipment
        note = MeasurEquipment.objects.get(equipment=instance_equipment)
    except:
        try:
            instance_equipment.testingequipment
            note = TestingEquipment.objects.get(equipment=instance_equipment)
        except:
            try:
                instance_equipment.helpingequipment
                note = HelpingEquipment.objects.get(equipment=instance_equipment)
            except:
                note = None
        
    if request.method == "POST":
        if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
            form = EquipmentKategoryUpdateForm(request.POST, instance=Equipment.objects.get(pk=str))
            if form.is_valid():  
                order = form.save(commit=False)
                if note:
                    note.delete()
                order.save()
                
                return redirect(f'/equipment/equipmentkategoryupdate/{str}/')
            else:
                messages.success(request, f' Раздел доступен только продвинутому пользователю')
                return redirect(f'/equipment/equipmentkategoryupdate/{str}/')
    else:
        form = EquipmentKategoryUpdateForm(instance=Equipment.objects.get(pk=str))
        
        data = {'form': form,
                'note': note, 
                }
        return render(request, 'equipment/equipment_kategory_red.html', data)



@login_required
def VerificationDeleteView(request, str):
    """для кнопки удаления поверки """
    """не выводит страницу, выполняет действие"""
    """path('verificationdelete/<str:str>/', views.VerificationDeleteView, name='verificationdelete'),"""

    for_a = Verificationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber

    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Verificationequipment.objects.get(pk=str)
            note.delete()
            try:
                find_ver = Verificationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save()    
            except:
                pass
            messages.success(request, 'Запись о поверке удалена!')
            return redirect(f'/equipment/measureequipment/verification/{a}/')            
        except:
            messages.success(request, 'Невозможно удалить')
            return redirect(f'/equipment/measureequipment/verification/{a}/')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect(f'/equipment/measureequipment/verification/{a}/')


@login_required
def CalibrationDeleteView(request, str):
    """для кнопки удаления калибровки """
    """не выводит страницу, выполняет действие"""
    """path('calibrationdelete/<str:str>/', views.CalibrationDeleteView, name='calibrationdelete'),"""
    for_a = Calibrationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber

    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Calibrationequipment.objects.get(pk=str)
            note.delete()
            try:
                find_ver = Calibrationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save() 
            except:
                pass
            messages.success(request, 'Запись о калибровке удалена!')
            return redirect(f'/equipment/measureequipment/calibration/{a}/')            
        except:
            messages.success(request, 'Невозможно удалить')
            return redirect(f'/equipment/measureequipment/calibration/{a}/')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect(f'/equipment/measureequipment/calibration/{a}/')


@login_required
def AttestationDeleteView(request, str):
    """для кнопки удаления аттестации """
    """не выводит страницу, выполняет действие"""
    """path('attestationdelete/<str:str>/', views.AttestationDeleteView, name='attestationdelete'),"""
    for_a = Attestationequipment.objects.get(pk=str)
    a=for_a.equipmentSM.equipment.exnumber
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            note = Attestationequipment.objects.get(pk=str)
            note.delete()
            try:
                find_ver = Attestationequipment.objects.filter(equipmentSM__equipment__exnumber=a).last()
                find_ver.save()
            except:
                pass
            messages.success(request, 'Запись об аттестации удалена!')
            return redirect(f'/equipment/testingequipment/attestation/{a}/')            
        except:
            messages.success(request, 'Невозможно удалить')
            return redirect(f'/equipment/testingequipment/attestation/{a}/')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect(f'/equipment/testingequipment/attestation/{a}/')


@login_required
def EcommentDeleteView(request, str):
    """для кнопки удаления комментария к оборудованию (записи в карточке прибора)"""
    """не выводит страницу, выполняет действие"""
    """path('ecommentdelete/<str:str>/', views.EcommentDeleteView, name='ecommentdelete'),"""
    note = CommentsEquipment.objects.get(pk=str)
    a = note.forNote.exnumber
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser or request.user.username == note.created_by:
        try:
            note.delete()
            messages.success(request, 'Комментарий удален!')
            return redirect(reverse('equipmentcomments', kwargs={'str': a}))           
        except:
            messages.success(request, 'Невозможно удалить!')
            return redirect(reverse('equipmentcomments', kwargs={'str': a}))
    else:
        messages.success(self.request, "Удаление доступно только продвинутому пользователю или автору записи")
        return redirect(reverse('equipmentcomments', kwargs={'str': a}))


@login_required
def PersonchangeDeleteView(request, str):
    """для кнопки удаления записи о смене ответственного за прибор"""
    """не выводит страницу, выполняет действие"""
    """path('personchangedelete/<str:str>/', views.PersonchangeDeleteView, name='personchangedelete'),"""
    
    note = Personchange.objects.get(pk=str)
    
    a = note.equipment.pk
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            note.delete()
            try:
                find_pc =Personchange.objects.filter(equipment__pk=a).last()
                find_pc.save()
            except:
                pass
            messages.success(request, 'Запись удалена!')
            return redirect(reverse('personchangelist', kwargs={'str': a}))           
        except:
            messages.success(request, 'Невозможно удалить!')
            return redirect(reverse('personchangelist', kwargs={'str': a}))
    else:
        messages.success(self.request, "Удаление доступно только продвинутому пользователю")
        return redirect(reverse('personchangelist', kwargs={'str': a}))


@login_required
def RoomchangeDeleteView(request, str):
    """для кнопки удаления записи о смене расположения прибора"""
    """не выводит страницу, выполняет действие"""
    """path('roomchangedelete/<str:str>/', views.RoomchangeDeleteView, name='roomchangedelete'),"""
    
    note = Roomschange.objects.get(pk=str)
    
    a = note.equipment.pk
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            note.delete()
            try:
                find_rc =Roomschange.objects.filter(equipment__pk=a).last()
                find_rc.save()
            except:
                pass
            messages.success(request, 'Запись удалена!')
            return redirect(reverse('roomchangelist', kwargs={'str': a}))           
        except:
            messages.success(request, 'Невозможно удалить!')
            return redirect(reverse('roomchangelist', kwargs={'str': a}))
    else:
        messages.success(self.request, "Удаление доступно только продвинутому пользователю")
        return redirect(reverse('roomchangelist', kwargs={'str': a}))


@login_required
def DocumentsDeleteView(request, str):
    """для кнопки удаления записи о документе оборудования"""
    """не выводит страницу, выполняет действие"""
    """path('documentsdelete/<str:str>/', views.DocumentsDeleteView, name='documentsdelete'),"""
    
    note = DocsCons.objects.get(pk=str)
    
    a = note.equipment.exnumber
    
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            note.delete()
            messages.success(request, 'Запись удалена!')
            return redirect(reverse('docsreg', kwargs={'str': a}))           
        except:
            messages.success(request, 'Невозможно удалить!')
            return redirect(reverse('docsreg', kwargs={'str': a}))
    else:
        messages.success(self.request, "Удаление доступно только продвинутому пользователю")
        return redirect(reverse('docsreg', kwargs={'str': a}))


@login_required
def RoomDeleteView(request, str):
    """для кнопки удаления комнаты"""
    """не выводит страницу, выполняет действие"""
    """path('roomdelete/<str:str>/', views.RoomDeleteView, name='roomdelete'),"""
    ruser=request.user.profile.userid
    if request.user.has_perm('equipment.add_equipment') or request.user.is_superuser:
        try:
            ruser=request.user.profile.userid
            note = Rooms.objects.filter(pointer=ruser).get(pk=str)
            note.delete()
            messages.success(request, 'Комната удалена!')
            return redirect('rooms')            
        except:
            messages.success(request, 'Невозможно удалить, возможно уже добавлен прибор с этой комнатой')
            return redirect('rooms')
    else:
        messages.success(self.request, "Раздел доступен только продвинутому пользователю")
        return redirect('manufacturerlist')
# блок 15 - массовая загрузка через EXEL





            
class UploadingModel(object):
    foreing_key_fields = [""]
    model = None
    number_objects = 0
    number_objects_del = 0
    number_rows = None

    def __init__(self, data):
        data=data
        self.uploaded_file = data.get("file")
        self.parsing()

    def getting_related_model(self, field_name):
        model = self.model
        related = model._meta.get_field(field_name).rel.to
        return related_model

    def getting_headers(self):
        l_verbose_name = []
        m_name = []
        for f in self.model._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers = dict()
        for column in range(s.ncols):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value)
            headers[column] = value
        return headers
            
    def parsing(self):
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        headers = self.getting_headers()
        print(headers)

        for row in range(1, s.nrows):
            row_dict = {}
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]
                if field_name == "id" and not value:
                    continue

                if field_name in self.foreing_key_fields:
                    related_model = self.getting_related_model(field_name)
                    print(related_model)

                    instance, created = related_model.objects.get_or_create(name=value)
                    value = instance
                row_dict[field_name] = value
            try:
                a = self.model.objects.create(**row_dict)
                if a.id:
                    self.number_objects+=1
                else:
                    pass
                self.number_rows = s.nrows - 1
                
            except:
                pass
        return True

class UploadingMeasurEquipmentCharakters(UploadingModel):
    model = MeasurEquipmentCharakters

class UploadingTestingEquipmentCharakters(UploadingModel):
    model = TestingEquipmentCharakters

class UploadingHelpingEquipmentCharakters(UploadingModel):
    model = HelpingEquipmentCharakters

from django.http import HttpResponse, request

class UploadingTwoModels(object):
    foreing_key_fields = [""]
    model = None
    model2 = None
    model3 = None
    number_objects = 0
    number_objects_del = 0
    number_objects_metehe = 0
    number_objects_char = 0
    number_rows = None
    kategory_e = None
    num_hc = 0
    num_e = 0

    
    def __init__(self, data):
        data=data
        self.uploaded_file = data.get("file")
        self.parsing()

    def getting_related_model(self, field_name):
        try:
            model = self.model
            related_model = model._meta.get_field(field_name).related_model
            return related_model
        except:
            raise Exception(f'проблема с производителем {field_name}')

    def getting_headers(self):
        l_verbose_name = []
        m_name = []
        for f in self.model._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers = dict()
        for column in range(self.num_hc, self.num_e):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value)
            headers[column] = value
        return headers

    def getting_headers_characters(self):
        l_verbose_name = []
        m_name = []
        for f in self.model2._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers_characters = dict()
        for column in range(self.num_hc):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value, dict())
            headers_characters[column] = value
        return headers_characters
            
    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        headers = self.getting_headers()
        headers_characters = self.getting_headers_characters()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict = {}
            row_dict_item_metehe = {}
            row_dict_room = {}
            row_dict_person = {}
            
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                a = str(value)
                b = a.find('.')
                if b != -1:
                    value = str(value)[0:b]
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                b, created = self.model2.objects.filter(pointer=pointer).get_or_create(**row_dict_characters)
                row_dict_item_metehe['charakters'] = b
                if created:
                    self.number_objects_char+=1
            except:
                raise Exception(f"проблема в создании/нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, self.num_e):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers[column]
                if field_name in self.foreing_key_fields:
                    related_model = self.getting_related_model(field_name)                 
                    instance, created = related_model.objects.get_or_create(companyName=value)
                    value = instance
                if field_name in ["price"] and value:
                    ind = value.find(",")
                    if ind != -1:
                        value = value.replace(",", ".")
                    try:
                        value = Decimal(value)
                    except:
                        value = 0
                row_dict[field_name] = value
                row_dict['kategory'] = self.kategory_e
                ahe = row_dict_characters['name'] 
                aheone = str(ahe)[0].upper()
                have_exnumber = aheone
                row_dict['exnumber'] = get_exnumber(have_exnumber, pointer)
            if row_dict['yearintoservice'] == "" or row_dict['yearintoservice'] == " " or len(row_dict['yearintoservice']) > 4 or not str(row_dict['yearintoservice']).isdigit():
                row_dict['yearintoservice'] = 0
            if not row_dict['yearmanuf'] or row_dict['yearmanuf'] == " " or len(row_dict['yearmanuf']) > 4 or not str(row_dict['yearmanuf']).isdigit():
                row_dict['yearmanuf'] = 0
            if not row_dict['price'] or not str(row_dict['price']).isdigit():
                row_dict['price'] = 0
            if row_dict['serviceneed'] != 0  or row_dict['serviceneed'] != 1 or row_dict['serviceneed'] != "0"  or row_dict['serviceneed'] != "1":
                row_dict['serviceneed'] = 1
            statuses = ['Э', 'РЕ', 'С', 'Р', 'Д']
            if row_dict['status'] not in statuses:
                row_dict['status'] = 'Э'

            try:
                a, e_created = self.model.objects.filter(pointer=pointer).get_or_create(**row_dict)
            except:
                try:
                    del row_dict['exnumber']
                    del row_dict['new']
                    del row_dict['pravo_have']
                    del row_dict['yearintoservice']
                    del row_dict['status']
                    del row_dict['serviceneed']
                    del row_dict['price']
                    del row_dict['invnumber']
                    del row_dict['pravo']
                    
                    a = self.model.objects.get(**row_dict)
                    e_created = 0
                except:
                    raise Exception(f"проблема в создании ЛО: {row_dict}")
                    

            if e_created:
                row_dict_item_metehe['equipment'] = a
                row_dict_room['equipment'] = a
                row_dict_person['equipment'] = a
                self.number_objects+=1
            else:
                pass

            if e_created:    
                try:
                    с = self.model3.objects.create(**row_dict_item_metehe)
                    if с.id:
                        self.number_objects_metehe+=1
                    else:
                        pass
                except:
                    raise Exception(f"проблема в создании единицы {self.kategory_e}: {row_dict_item_metehe}")

            if e_created:
                for column in range(self.num_e, self.num_e + 1):
                    value = s.cell(row, column).value
                    value = get_rid_point(value)
                    field_name = 'roomnumber'
                    related_model = Rooms         
                    instance_room, created = related_model.objects.filter(pointer=pointer).get_or_create(roomnumber=value)
                    value = instance_room                                            
                    row_dict_room['roomnumber'] = value
                    
                    try:
                        Roomschange.objects.get_or_create(**row_dict_room)
                    except:
                        raise Exception(f"проблема в создании Комнаты: {row_dict_room}")

                for column in range(self.num_e + 1, self.num_e + 2):
                    value = s.cell(row, column).value
                    field_name = 'person'
                    related_model = User
                    try:
                        instance_user = ''
                        instance_user = User.objects.filter(profile__userid=pointer).get(profile__short_name=value)                       
                        row_dict_person[field_name] = instance_user
                        Personchange.objects.get_or_create(**row_dict_person)
                    except:
                        pass

                for column in range(self.num_e + 2, self.num_e + 3):
                    value = s.cell(row, column).value
                    if value:
                        instance.country = value
                        instance.save()

                for column in range(self.num_e + 3, self.num_e + 4):
                    value = s.cell(row, column).value
                    if value:
                        с.aim = value
                        с.save()

                try:
                    for column in range(self.num_e + 4, self.num_e + 5):
                        value = s.cell(row, column).value
                        if value:
                            с.analited_objects = value
                            с.save()
                except:
                    pass
                    

                             
        self.number_objects = f'{self.number_objects} единиц ЛО, {self.number_objects_char} характеристик {self.kategory_e}, {self.number_objects_metehe} единиц {self.kategory_e}'
        self.number_rows = s.nrows - 1
        return True


class UploadingEquipment_MeasurEquipment(UploadingTwoModels):
    model = Equipment
    model2 = MeasurEquipmentCharakters
    model3 = MeasurEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "СИ"
    num_hc = 3
    num_e = 15

class UploadingEquipment_TestingEquipment(UploadingTwoModels):
    model = Equipment
    model2 = TestingEquipmentCharakters
    model3 = TestingEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "ИО"
    num_hc = 2
    num_e = 13

class UploadingEquipment_HelpingEquipment(UploadingTwoModels):
    model = Equipment
    model2 = HelpingEquipmentCharakters
    model3 = HelpingEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "ВО"
    num_hc = 2
    num_e = 13



class UploadingMetrologyForEquipment(object):
    foreing_key_fields = ["verificator", "manufacturer"] 
    model_metrology = None
    model_CH = MeasurEquipmentCharakters
    model_objMETEHE = None
    number_rows = 0
    number_objects = 0
    number_objects_del = 0
    kategory_e = None
    num_hc = 0
    num_e = 0
   
    def __init__(self, data):
        data=data
        self.uploaded_file = data.get("file")
        self.parsing()

    def getting_related_model(self, field_name, model):
        try:
            related_model = model._meta.get_field(field_name).related_model
            return related_model
        except:
            pass
            # raise Exception(f'проблема с производителем {field_name}')

    def getting_headers_model_metrology(self):
        l_verbose_name = []
        m_name = []
        for f in self.model_metrology._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                raise
                # pass
        s = self.s
        headers_model_metrology = dict()
        for column in range(self.num_e, s.ncols):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                # pass
                raise KeyError(value)
            headers_model_metrology[column] = value
        return headers_model_metrology

    def getting_headers_characters(self):
        l_verbose_name = []
        m_name = []
        for f in self.model_CH._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers_characters = dict()
        for column in range(self.num_hc):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value, dict())
            headers_characters[column] = value
        return headers_characters

    def getting_headers_equipment(self):
        l_verbose_name = []
        m_name = []
        for f in Equipment._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers_equipment = dict()
        for column in range(self.num_hc, self.num_e):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value, dict())
            headers_equipment[column] = value
        return headers_equipment
            
    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        
        headers_characters = self.getting_headers_characters()
        headers_model_metrology = self.getting_headers_model_metrology()
        headers_equipment = self.getting_headers_equipment()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict_equipment = {}
            row_dict_METEHE = {}
            row_dict_metrology = {}

            
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                a = str(value)
                b = a.find('.')
                if b != -1:
                    value = str(value)[0:b]
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                find_charakters = self.model_CH.objects.filter(pointer=pointer).get(**row_dict_characters)
                row_dict_METEHE['charakters'] = find_charakters
                find_charakters_bool = True
            except:
                find_charakters_bool = False
                pass
                # raise Exception(f"проблема в нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, self.num_e):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers_equipment[column]
                if field_name in self.foreing_key_fields:
                    model = Equipment
                    related_model = self.getting_related_model(field_name, model)                 
                    instance = related_model.objects.get(companyName=value)
                    value = instance                          
                row_dict_equipment[field_name] = value
            try:
                if not row_dict_equipment['yearmanuf']:
                    row_dict_equipment['yearmanuf'] = "0"
                find_equipment = Equipment.objects.filter(pointer=pointer).get(**row_dict_equipment)
                row_dict_METEHE['equipment'] = find_equipment
                find_equipment_bool = True
            except:
                find_equipment_bool = False
                pass
                # raise Exception(f"проблема в нахождении единицы ЛО: {row_dict_equipment}")

            if find_equipment_bool and find_charakters_bool:
                try:
                    equipmentSM  = self.model_objMETEHE.objects.filter(pointer=pointer).get(**row_dict_METEHE)
                    equipmentSM_bool = True
                except:
                    equipmentSM_bool = False
                    pass
                    # raise Exception(f"проблема в нахождении единицы {self.kategory_e}: {row_dict_METEHE}")
            
            if find_equipment_bool and find_charakters_bool and equipmentSM_bool:
                for column in range(self.num_e, s.ncols):                  
                    value = s.cell(row, column).value
                                    
                    field_name = headers_model_metrology[column]
                    if field_name in self.foreing_key_fields:
                        model = self.model_metrology
                        related_model = self.getting_related_model(field_name, model)
                        instance_verificator, created = related_model.objects.get_or_create(companyName=value)
                        value = instance_verificator
                    if field_name in ["date", "datedead", "dateorder", "dateordernew"] and value:
                        value = get_dateformat_django(value)
                    if field_name in ["price"] and value:
                        ind = value.find(",")
                        if ind != -1:
                            value = value.replace(",", ".")
                        value = Decimal(value)
                    
                    if value or value == 0:
                        row_dict_metrology[field_name] = value
                row_dict_metrology['equipmentSM'] = equipmentSM
                try:
                    a, m_created = self.model_metrology.objects.filter(pointer=pointer).get_or_create(**row_dict_metrology)
                    if m_created:
                        self.number_objects+=1
                except:
                    pass
                    # raise Exception(f"проблема в добавлении сведений о поверке/калибровке/аттестации: {row_dict_metrology}")
                                        
        self.number_rows = s.nrows - 1
        return True


class Uploading_Verificationequipment(UploadingMetrologyForEquipment):
    model_metrology = Verificationequipment
    model_CH = MeasurEquipmentCharakters
    model_objMETEHE = MeasurEquipment
    kategory_e = "СИ"
    num_hc = 3
    num_e = 6

class Uploading_Calibrationequipment(UploadingMetrologyForEquipment):
    model_metrology = Calibrationequipment
    model_CH = MeasurEquipmentCharakters
    model_objMETEHE = MeasurEquipment
    kategory_e = "СИ"
    num_hc = 3
    num_e = 6

class Uploading_Attestationequipment(UploadingMetrologyForEquipment):
    model_metrology = Attestationequipment
    model_CH = TestingEquipmentCharakters
    model_objMETEHE = TestingEquipment
    kategory_e = "ИО"
    num_hc = 2
    num_e = 5
    

class DeleteMetrologyForEquipment(UploadingMetrologyForEquipment):
    # для удаления поверки калибровки и аттестации по загрузке ексель файла, родительский класс    
    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        
        headers_characters = self.getting_headers_characters()
        headers_model_metrology = self.getting_headers_model_metrology()
        headers_equipment = self.getting_headers_equipment()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict_equipment = {}
            row_dict_METEHE = {}
            row_dict_metrology = {}

            
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                a = str(value)
                b = a.find('.')
                if b != -1:
                    value = str(value)[0:b]
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                find_charakters = self.model_CH.objects.filter(pointer=pointer).get(**row_dict_characters)
                row_dict_METEHE['charakters'] = find_charakters
                find_charakters_bool = True
            except:
                find_charakters_bool = False
                pass
                # raise Exception(f"проблема в нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, self.num_e):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers_equipment[column]
                if field_name in self.foreing_key_fields:
                    model = Equipment
                    related_model = self.getting_related_model(field_name, model)                 
                    instance = related_model.objects.get(companyName=value)
                    value = instance                          
                row_dict_equipment[field_name] = value
            try:
                if not row_dict_equipment['yearmanuf']:
                    row_dict_equipment['yearmanuf'] = "0"
                find_equipment = Equipment.objects.filter(pointer=pointer).get(**row_dict_equipment)
                row_dict_METEHE['equipment'] = find_equipment
                find_equipment_bool = True
            except:
                find_equipment_bool = False
                pass
                # raise Exception(f"проблема в нахождении единицы ЛО: {row_dict_equipment}")

            if find_equipment_bool and find_charakters_bool:
                try:
                    equipmentSM  = self.model_objMETEHE.objects.filter(pointer=pointer).get(**row_dict_METEHE)
                    equipmentSM_bool = True
                except:
                    equipmentSM_bool = False
                    pass
                    # raise Exception(f"проблема в нахождении единицы {self.kategory_e}: {row_dict_METEHE}")
            
            if find_equipment_bool and find_charakters_bool and equipmentSM_bool:
                for column in range(self.num_e, s.ncols):                  
                    value = s.cell(row, column).value
                                    
                    field_name = headers_model_metrology[column]
                    if field_name in self.foreing_key_fields:
                        model = self.model_metrology
                        related_model = self.getting_related_model(field_name, model)
                        instance_verificator, created = related_model.objects.get_or_create(companyName=value)
                        value = instance_verificator
                    if field_name in ["date", "datedead", "dateorder", "dateordernew"] and value:
                        value = get_dateformat_django(value)
                    if field_name in ["price"] and value:
                        ind = value.find(",")
                        if ind != -1:
                            value = value.replace(",", ".")
                        value = Decimal(value)
                    
                    if value or value == 0:
                        row_dict_metrology[field_name] = value
                row_dict_metrology['equipmentSM'] = equipmentSM
                try:
                    note = self.model_metrology.objects.filter(pointer=pointer).get(**row_dict_metrology)
                    for_b = self.model_metrology.objects.get(pk=note.pk)
                    b = for_b.equipmentSM.equipment.exnumber               
                    note.delete()
                    self.number_objects_del += 1
                    try:
                        find_ver = self.model_metrology.objects.filter(equipmentSM__equipment__exnumber=b).last()
                        find_ver.save()
                    except:
                        equipmentSM.newdatedead = ''
                        equipmentSM.newdateorder = ''
                        equipmentSM.newarshin = ''
                        equipmentSM.newcertnumber = ''
                        equipmentSM.newprice = '0'
                        equipmentSM.newstatusver = ''
                        equipmentSM.newverificator = ''
                        equipmentSM.newplace = ''
                        equipmentSM.newnote = ''
                        equipmentSM.newyear = ''
                        equipmentSM.newdateordernew = ''
                        equipmentSM.newhaveorder = False    
                        equipmentSM.save()
                except:
                    # raise
                    pass

        self.number_rows = s.nrows - 1
        return True

class Delete_Verificationequipment(DeleteMetrologyForEquipment):
    model_metrology = Verificationequipment
    model_CH = MeasurEquipmentCharakters
    model_objMETEHE = MeasurEquipment
    kategory_e = "СИ"
    num_hc = 3
    num_e = 6

class Delete_Calibrationequipment(DeleteMetrologyForEquipment):
    model_metrology = Calibrationequipment
    model_CH = MeasurEquipmentCharakters
    model_objMETEHE = MeasurEquipment
    kategory_e = "СИ"
    num_hc = 3
    num_e = 6

class Delete_Attestationequipment(DeleteMetrologyForEquipment):
    model_metrology = Attestationequipment
    model_CH = TestingEquipmentCharakters
    model_objMETEHE = TestingEquipment
    kategory_e = "ИО"
    num_hc = 2
    num_e = 5


class DeleteTwoModels(UploadingTwoModels):       
    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        headers = self.getting_headers()
        headers_characters = self.getting_headers_characters()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict = {}
            row_dict_item_metehe = {}
            row_dict_room = {}
            row_dict_person = {}
            
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                a = str(value)
                b = a.find('.')
                if b != -1:
                    value = str(value)[0:b]
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                b = self.model2.objects.filter(pointer=pointer).get(**row_dict_characters)
                row_dict_item_metehe['charakters'] = b
            except:
                raise Exception(f"проблема в нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, self.num_e):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers[column]
                if field_name in self.foreing_key_fields:
                    related_model = self.getting_related_model(field_name)                 
                    instance = related_model.objects.get(companyName=value)
                    value = instance
                if field_name in ["price"] and value:
                    ind = value.find(",")
                    if ind != -1:
                        value = value.replace(",", ".")
                    try:
                        value = Decimal(value)
                    except:
                        value = 0
                row_dict[field_name] = value
                row_dict['kategory'] = self.kategory_e                     
            try:
                del row_dict['new']
                del row_dict['pravo_have']
                del row_dict['yearintoservice']
                del row_dict['status']
                del row_dict['serviceneed']
                del row_dict['price']
                del row_dict['invnumber']
                del row_dict['pravo']
                a = self.model.objects.filter(pointer=pointer).get(**row_dict)
                row_dict_item_metehe['equipment'] = a

            except:
                pass
                # raise Exception(f"проблема в нахождении ЛО: {row_dict}")
            try:
                c = self.model3.objects.get(**row_dict_item_metehe)
                c.delete()
                a.delete()
                self.number_objects_del+=1
            except:
                pass
                # raise Exception(f"проблема в удалении единицы {self.kategory_e}: {row_dict_item_metehe}")
                    
        self.number_objects_del = f'{self.number_objects_del} единиц ЛО, удалено {self.number_objects_del} единиц {self.kategory_e}'
        self.number_rows = s.nrows - 1
        return True


class Delete_Equipment_MeasurEquipment(DeleteTwoModels):
    model = Equipment
    model2 = MeasurEquipmentCharakters
    model3 = MeasurEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "СИ"
    num_hc = 3
    num_e = 15

class Delete_Equipment_TestingEquipment(DeleteTwoModels):
    model = Equipment
    model2 = TestingEquipmentCharakters
    model3 = TestingEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "ИО"
    num_hc = 2
    num_e = 13

class Delete_Equipment_HelpingEquipment(DeleteTwoModels):
    model = Equipment
    model2 = HelpingEquipmentCharakters
    model3 = HelpingEquipment
    foreing_key_fields = ["manufacturer"]
    kategory_e = "ВО"
    num_hc = 2
    num_e = 13

class Delete_Model(UploadingModel):
    def parsing(self):
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        headers = self.getting_headers()

        for row in range(1, s.nrows):
            row_dict = {}
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]
                row_dict[field_name] = value
            try:
                a = self.model.objects.get(**row_dict)
                if a.id:
                    self.number_objects_del+=1
                a.delete()
            except:
                pass
        self.number_rows = s.nrows - 1
        return True

class Delete_MeasurEquipmentCharakters(Delete_Model):
    model = MeasurEquipmentCharakters

class Delete_TestingEquipmentCharakters(Delete_Model):
    model = TestingEquipmentCharakters

class Delete_HelpingEquipmentCharakters(Delete_Model):
    model = HelpingEquipmentCharakters

# дополнительные загрузки и удаления
class Uploading_ServiceEquipment(object):
    model_CH = MeasurEquipmentCharakters
    model_service = ServiceEquipmentME
    number_rows = 0
    number_objects = 0
    number_objects_del = 0
    kategory_e = "СИ"
    num_hc = 3
   
    def __init__(self, data):
        data=data
        self.uploaded_file = data.get("file")
        self.parsing()


    def getting_headers_service(self):
        l_verbose_name = []
        m_name = []
        for f in self.model_service._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers_service = dict()
        for column in range(self.num_hc, s.ncols):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                pass
                # raise KeyError(value)
            headers_service[column] = value
        return headers_service

    def getting_headers_characters(self):
        l_verbose_name = []
        m_name = []
        for f in self.model_CH._meta.get_fields():
            try:
                l_verbose_name.append(f.verbose_name)
                m_name.append(f.name)
            except:
                pass
        s = self.s
        headers_characters = dict()
        for column in range(self.num_hc):
            value = s.cell(0, column).value
            try:
                value in l_verbose_name
                a = l_verbose_name.index(value)
                value = m_name[a] 
            except:
                raise KeyError(value, dict())
            headers_characters[column] = value
        return headers_characters
            
    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        
        headers_service = self.getting_headers_service()
        headers_characters = self.getting_headers_characters()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict_service = {}
           
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                find_charakters = self.model_CH.objects.filter(pointer=pointer).get(**row_dict_characters)
                row_dict_service['charakters'] = find_charakters
            except:
                pass
                # raise Exception(f"проблема в нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, s.ncols):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers_service[column]                        
                row_dict_service[field_name] = value
            try:   
                se = self.model_service.objects.filter(pointer=pointer).create(**row_dict_service)
                if se.pk:
                    self.number_objects += 1
            except:
                pass
                # raise Exception(f"проблема в создании ТО: {row_dict_equipment}")
                                        
        self.number_rows = s.nrows - 1
        return True

class Uploading_ServiceEquipment_MeasurEquipment(Uploading_ServiceEquipment):
    model_CH = MeasurEquipmentCharakters
    model_service = ServiceEquipmentME
    kategory_e = "СИ"
    num_hc = 3

class Uploading_ServiceEquipment_TestingEquipment(Uploading_ServiceEquipment):
    model_CH = TestingEquipmentCharakters
    model_service = ServiceEquipmentTE
    kategory_e = "ИО"
    num_hc = 2

class Uploading_ServiceEquipment_HelpingEquipment(Uploading_ServiceEquipment):
    model_CH = HelpingEquipmentCharakters
    model_service = ServiceEquipmentHE
    kategory_e = "ВО"
    num_hc = 2


class Delete_ServiceEquipment(Uploading_ServiceEquipment):

    def parsing(self):
        pointer = get_current_user().profile.userid
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s
        
        headers_service = self.getting_headers_service()
        headers_characters = self.getting_headers_characters()

        for row in range(1, s.nrows):
            row_dict_characters = {}
            row_dict_service = {}
           
            for column in range(self.num_hc):
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name_characters = headers_characters[column]
                row_dict_characters[field_name_characters] = value
            try:   
                find_charakters = self.model_CH.objects.filter(pointer=pointer).get(**row_dict_characters)
                row_dict_service['charakters'] = find_charakters
            except:
                pass
                # raise Exception(f"проблема в нахождении характеристик {self.kategory_e}: {row_dict_characters}")

            for column in range(self.num_hc, s.ncols):                  
                value = s.cell(row, column).value
                value = get_rid_point(value)
                field_name = headers_service[column]                        
                row_dict_service[field_name] = value
            try:   
                se = self.model_service.objects.filter(pointer=pointer).get(**row_dict_service)
                se.delete()
                self.number_objects_del += 1
            except:
                pass
                # raise Exception(f"проблема в удалении ТО: {row_dict_equipment}")
                                        
        self.number_rows = s.nrows - 1
        return True



class Delete_ServiceEquipment_MeasurEquipment(Delete_ServiceEquipment):
    model_CH = MeasurEquipmentCharakters
    model_service = ServiceEquipmentME
    kategory_e = "СИ"
    num_hc = 3

class Delete_ServiceEquipment_TestingEquipment(Delete_ServiceEquipment):
    model_CH = TestingEquipmentCharakters
    model_service = ServiceEquipmentTE
    kategory_e = "ИО"
    num_hc = 2

class Delete_ServiceEquipment_HelpingEquipment(Delete_ServiceEquipment):
    model_CH = HelpingEquipmentCharakters
    model_service = ServiceEquipmentHE
    kategory_e = "ВО"
    num_hc = 2


def BulkDownload(request):
    """выводит страницу загрузки через EXEL"""
    """path('bulkdownload/', views.BulkDownloadView, name='bulkdownload'),"""  
    """template_name = URL + '/bulk_download.html'"""

    if request.POST:        
        MeasurEquipmentCharakters_file = request.FILES.get('MeasurEquipmentCharakters_file')
        TestingEquipmentCharakters_file = request.FILES.get('TestingEquipmentCharakters_file')
        HelpingEquipmentCharakters_file = request.FILES.get('HelpingEquipmentCharakters_file')

        MeasurEquipment_Equipment_file = request.FILES.get('MeasurEquipment_Equipment_file')
        TestingEquipment_Equipment_file = request.FILES.get('TestingEquipment_Equipment_file')
        HelpingEquipment_Equipment_file = request.FILES.get('HelpingEquipment_Equipment_file')

        Verificationequipment_file = request.FILES.get('Verificationequipment_file')
        Calibrationequipment_file = request.FILES.get('Calibrationequipment_file')
        Attestationequipment_file = request.FILES.get('Attestationequipment_file')

        MeasurEquipmentCharakters_file_del = request.FILES.get('MeasurEquipmentCharakters_file_del')
        TestingEquipmentCharakters_file_del = request.FILES.get('TestingEquipmentCharakters_file_del')
        HelpingEquipmentCharakters_file_del = request.FILES.get('HelpingEquipmentCharakters_file_del')

        MeasurEquipment_Equipment_file_del = request.FILES.get('MeasurEquipment_Equipment_file_del')
        TestingEquipment_Equipment_file_del = request.FILES.get('TestingEquipment_Equipment_file_del')
        HelpingEquipment_Equipment_file_del = request.FILES.get('HelpingEquipment_Equipment_file_del')

        Verificationequipment_file_del = request.FILES.get('Verificationequipment_file_del')
        Calibrationequipment_file_del = request.FILES.get('Calibrationequipment_file_del')
        Attestationequipment_file_del = request.FILES.get('Attestationequipment_file_del')

        ServiceEquipment_MeasurEquipment_file = request.FILES.get('ServiceEquipment_MeasurEquipment_file')
        ServiceEquipment_TestingEquipment_file = request.FILES.get('ServiceEquipment_TestingEquipment_file')
        ServiceEquipment_HelpingEquipment_file = request.FILES.get('ServiceEquipment_HelpingEquipment_file')

        ServiceEquipment_MeasurEquipment_file_del = request.FILES.get('ServiceEquipment_MeasurEquipment_file_del')
        ServiceEquipment_TestingEquipment_file_del = request.FILES.get('ServiceEquipment_TestingEquipment_file_del')
        ServiceEquipment_HelpingEquipment_file_del = request.FILES.get('ServiceEquipment_HelpingEquipment_file_del')
                
        uploading_file_fake = 1

        # для загрузки
        if MeasurEquipmentCharakters_file:
            try:
                uploading_file = UploadingMeasurEquipmentCharakters({'file': MeasurEquipmentCharakters_file})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики СИ' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')
                

        elif HelpingEquipmentCharakters_file:
            try:
                uploading_file = UploadingHelpingEquipmentCharakters({'file': HelpingEquipmentCharakters_file})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики ВО' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')
                
        elif TestingEquipmentCharakters_file:
            try:
                uploading_file = UploadingTestingEquipmentCharakters({'file': TestingEquipmentCharakters_file})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики ИО' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')

        elif MeasurEquipment_Equipment_file:
            try:
                uploading_file = UploadingEquipment_MeasurEquipment({'file': MeasurEquipment_Equipment_file})
            except:
                messages.success(request, "Неверно заполнен файл 'единица ЛО и СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif TestingEquipment_Equipment_file:
            try:
                uploading_file = UploadingEquipment_TestingEquipment({'file': TestingEquipment_Equipment_file})
            except:
                
                messages.success(request, "Неверно заполнен файл 'единица ЛО и ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif HelpingEquipment_Equipment_file:
            try:
                uploading_file = UploadingEquipment_HelpingEquipment({'file': HelpingEquipment_Equipment_file})
            except:
                messages.success(request, "Неверно заполнен файл 'единица ЛО и ВО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif Verificationequipment_file:
            try:
                uploading_file = Uploading_Verificationequipment({'file': Verificationequipment_file})
            except:
                raise
                # messages.success(request, "Неверно заполнен файл 'Поверка СИ' (вероятно проблема в названиях или в порядке столбцов)")
                # return redirect('bulkdownload')

        elif Calibrationequipment_file:
            try:
                uploading_file = Uploading_Calibrationequipment({'file': Calibrationequipment_file})
            except:
                
                messages.success(request, "Неверно заполнен файл 'Калибровка СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif Attestationequipment_file:
            try:
                uploading_file = Uploading_Attestationequipment({'file': Attestationequipment_file})
            except:
                
                messages.success(request, "Неверно заполнен файл 'Аттестация ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif ServiceEquipment_MeasurEquipment_file:
            try:
                uploading_file = Uploading_ServiceEquipment_MeasurEquipment({'file': ServiceEquipment_MeasurEquipment_file})
            except:
                
                messages.success(request, "Неверно заполнен файл 'ТО СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif ServiceEquipment_TestingEquipment_file:
            try:
                uploading_file = Uploading_ServiceEquipment_TestingEquipment({'file': ServiceEquipment_TestingEquipment_file})
            except:
                
                messages.success(request, "Неверно заполнен файл 'ТО ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif ServiceEquipment_HelpingEquipment_file:
            try:
                uploading_file = Uploading_ServiceEquipment_HelpingEquipment({'file': ServiceEquipment_HelpingEquipment_file})
            except:
                messages.success(request, "Неверно заполнен файл 'ТО ВО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        # для удаления
        elif MeasurEquipmentCharakters_file_del:
            try:
                uploading_file = Delete_MeasurEquipmentCharakters({'file': MeasurEquipmentCharakters_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики СИ' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')
                

        elif HelpingEquipmentCharakters_file_del:
            try:
                uploading_file = Delete_HelpingEquipmentCharakters({'file': HelpingEquipmentCharakters_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики ВО' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')
                
        elif TestingEquipmentCharakters_file_del:
            try:
                uploading_file = Delete_TestingEquipmentCharakters({'file': TestingEquipmentCharakters_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'Характеристики ИО' (вероятно проблема в названиях столбцов)")
                return redirect('bulkdownload')

        elif MeasurEquipment_Equipment_file_del:
            try:
                uploading_file = Delete_Equipment_MeasurEquipment({'file': MeasurEquipment_Equipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'единица ЛО и СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif TestingEquipment_Equipment_file_del:
            try:
                uploading_file = Delete_Equipment_TestingEquipment({'file': TestingEquipment_Equipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'единица ЛО и ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif HelpingEquipment_Equipment_file_del:
            try:
                uploading_file = Delete_Equipment_HelpingEquipment({'file': HelpingEquipment_Equipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'единица ЛО и ВО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif Verificationequipment_file_del:
            try:
                uploading_file = Delete_Verificationequipment({'file': Verificationequipment_file_del})
            except:
                raise
                # messages.success(request, "Неверно заполнен файл 'Поверка СИ' (вероятно проблема в названиях или в порядке столбцов)")
                # return redirect('bulkdownload')

        elif Calibrationequipment_file_del:
            try:
                uploading_file = Delete_Calibrationequipment({'file': Calibrationequipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'Калибровка СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif Attestationequipment_file_del:
            try:
                uploading_file = Delete_Attestationequipment({'file': Attestationequipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'Аттестация ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')


        elif ServiceEquipment_MeasurEquipment_file_del:
            try:
                uploading_file = Delete_ServiceEquipment_MeasurEquipment({'file': ServiceEquipment_MeasurEquipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'ТО СИ' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif ServiceEquipment_TestingEquipment_file_del:
            try:
                uploading_file = Delete_ServiceEquipment_TestingEquipment({'file': ServiceEquipment_TestingEquipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'ТО ИО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')

        elif ServiceEquipment_HelpingEquipment_file_del:
            try:
                uploading_file = Delete_ServiceEquipment_HelpingEquipment({'file': ServiceEquipment_HelpingEquipment_file_del})
            except:
                messages.success(request, "Неверно заполнен файл 'ТО ВО' (вероятно проблема в названиях или в порядке столбцов)")
                return redirect('bulkdownload')
                
        elif uploading_file_fake:
            try:
               messages.success(request, "Сначала выберите файл EXEL.xls")
            except:                
                messages.success(request, "Сначала выберите файл EXEL.xls")
                return redirect('bulkdownload')
         
        try:           
            number_objects = uploading_file.number_objects
            number_rows = uploading_file.number_rows
            number_objects_del = uploading_file.number_objects_del
        
            if uploading_file:
                if number_objects and number_rows:
                    messages.success(request, f"Файл успешно загружен, добавлено {number_objects} -  из {number_rows} строк файла EXEL")
                elif number_objects_del and number_rows:
                    messages.success(request, f"Файл успешно загружен, удалено {number_objects_del} записей из бд -  из {number_rows} строк файла EXEL")
                else:
                    messages.success(request, f"Ничего не добавилось (так как файл пустой,  не заполнены или неверно заполнены обязательные столбцы или такие объекты уже есть в базе данных)")      

            else:
                messages.success(request, "Файл не загружен")
        except:
            pass
             # messages.success(request, "Сначала выберите файл EXEL.xls")
            
    return render(request, URL + '/bulk_download.html', locals())
