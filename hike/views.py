from datetime import date

from django.shortcuts import render
import pandas as pd
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView

from django.db.models import Q


from .models import *
from .forms import *
from .constants import *
from django.views.generic import ListView, TemplateView, CreateView, UpdateView

from django import forms




now = date.today()

from django.views import View
from django.shortcuts import render
from django.core.exceptions import PermissionDenied

class PersonalPanelView(View):
    def get(self, request):
        # Строгая проверка: очищаем от пробелов и переводим в нижний регистр
        if not request.user.is_authenticated or request.user.username.strip().lower() != 'labjournal':
            raise PermissionDenied
            
        # Рендерим личный раздел из папки hike
        return render(request, 'hike/personal.html')



class ExampleTemplateView(TemplateView):
    template_name = 'hike/example.html'
    def get_context_data(self, **kwargs):
        context = super(ExampleTemplateView,self).get_context_data(**kwargs)
        context["categories"] = {'первая', 'вторая', 'третья', 'четвертая',}
        context["values"] = {'1', '2', '3', '4',}
        context["table_data"] = {'11', '22', '33', '44',}
        return context

from django.shortcuts import render
from .models import Hike, RouteFeature  # Убедитесь, что модель импортирована

# Добавьте получение особенностей в ListView
class HikeAllListView(ListView):
    """ Выводит список всех маршрутов """
    model = Hike
    template_name = 'hike/mainlist.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6
    
    def get_context_data(self, **kwargs):
        context = super(HikeAllListView, self).get_context_data(**kwargs)
        context['form'] = SearchForm() 
        context['pk'] = 0
        context['qk'] = 0
        context['rk'] = 0
        context['fk'] = 0  # 0 означает, что фильтр по особенностям выключен
        context['all_features'] = RouteFeature.objects.all()  # Передаем список всех особенностей
        return context


# Новая функция фильтра по особенностям маршрута
def featurehikefilterview(request, fk):
    """ Фильтр маршрутов по конкретной особенности """
    if fk == 0:
        objects = Hike.objects.all().order_by('-pk')
    else:
        # Фильтруем походы, у которых есть связь с особенностью по ее первичному ключу (id)
        objects = Hike.objects.filter(features__pk=fk).order_by('-pk')
        
    form = SearchForm() 
    pk = 0
    qk = 0
    rk = 0
    all_features = RouteFeature.objects.all()  # Снова подгружаем для отображения в списке
    
    return render(request, "hike/mainlist.html", {
        'objects': objects, 
        'form': form, 
        'pk': pk, 
        'qk': qk, 
        'rk': rk, 
        'fk': fk,  # Передаем ID выбранной особенности
        'all_features': all_features
    })




class BMAllListView(View):
    """ Выводит список всех закладок на разные темы """

    def get(self, request):
        objects = Bookmarks.objects.filter(done=False).order_by('-pk')
        form = UdateForm()
        sform = SearchForm() 
        return render(request, 'hike/bm.html', {'form': form, 'sform': sform, 'objects': objects, })

    def post(self, request, *args, **kwargs):
        object_ids = request.POST.getlist('my_object')
        note1 = Bookmarks.objects.get(id=168) 
        form = UdateForm(request.POST, instance=note1)
        if form.is_valid():
            order = form.save(commit=False)
            return redirect('bm')




class BMSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по истории Карелии """

    template_name = 'hike/bm.html'

    def get_context_data(self, **kwargs):
        context = super(BMSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET.get('searchword', '')


        context['form'] = UdateForm()
        context['sform'] = SearchForm() 
        if searchword:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Bookmarks.objects.\
            filter(Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            
        return context



class ITAllListView(ListView):
    """ Выводит список всех закладок по айти """
    model = Itbookmarks
    template_name = 'hike/it.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6
    def get_context_data(self,**kwargs):
        context = super(ITAllListView,self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

class KareliahistoryAllListView(ListView):
    """ Выводит список всех закладок по истории Карелии """
    model = Kareliahistory
    template_name = 'hike/kareliahistory.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6
    def get_context_data(self,**kwargs):
        context = super(KareliahistoryAllListView,self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

class KareliahistorySearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по истории Карелии """

    template_name = 'hike/kareliahistory.html'

    def get_context_data(self, **kwargs):
        context = super(KareliahistorySearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET.get('searchword', '')

        context['form'] = SearchForm()
        if searchword:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Kareliahistory.objects.\
            filter(Q(title__icontains=searchword)|Q(title__icontains=searchword1)).order_by('pk') | Kareliahistory.objects.\
            filter(Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            
        return context


class HikeStrView(CreateView):
    """ выводит отдельный маршрут """
    model = Hike
    template_name = 'hike/indilist.html'
    form_class = CommentCreationForm

    def get_object(self, queryset=None):
        return Hike.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(HikeStrView, self).get_context_data(**kwargs)
        comments = Comments.objects.filter(forNote=self.kwargs['pk']).order_by("pk")
        obj = Hike.objects.get(pk=self.kwargs.get("pk"))
        context['form'] = CommentCreationForm()
        context['comments'] = comments
        context['obj'] = obj

        return context

    def form_valid(self, form):
        order = form.save(commit=False)
        order.forNote = Hike.objects.get(pk=self.kwargs['pk'])
        order.save()
        return super().form_valid(form)



        

class ITSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по закладкам айти """

    template_name = 'hike/it.html'

    def get_context_data(self, **kwargs):
        context = super(ITSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET.get('searchword', '')

        if searchword:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Itbookmarks.objects.\
            filter(Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context



def filterview(request, pk):
    """ Фильтр заметок по темам """
    objects = Bookmarks.objects.filter(done=False)
    for i in range(len(TYPE)):
        s = TYPE[i][0]
        if pk == i:
            objects = objects.filter(type=s).order_by('-pk')
            form = UdateForm()
            sform = SearchForm() 

    return render(request,  "hike/bm.html", {'objects': objects, 'form':form, 'sform':sform})






class FamilyListView(ListView):
    """ Выводит список всех закладок по истории семьи """
    model = Family
    template_name = 'hike/family.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6
    def get_context_data(self,**kwargs):
        context = super(FamilyListView,self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

class FamilySearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по истории семьи """

    template_name = 'hike/family.html'

    def get_context_data(self, **kwargs):
        context = super(FamilySearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET.get('searchword', '')

        if searchword:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Family.objects.\
            filter(Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context


class ChemistryListView(ListView):
    """ Выводит список всех закладок по химии """
    model = Chemistry
    template_name = 'hike/chemistry.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6
    def get_context_data(self,**kwargs):
        context = super(ChemistryListView,self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

class ChemistrySearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по химии """

    template_name = 'hike/chemistry.html'

    def get_context_data(self, **kwargs):
        context = super(ChemistrySearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET.get('searchword', '')

        if searchword:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Chemistry.objects.\
            filter(Q(text__icontains=searchword)|Q(text__icontains=searchword1)|Q(type__icontains=searchword)|Q(type__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context


class HistoryListView(TemplateView):
    """ Выводит информацию для таблицы по истории """
    template_name = 'hike/history.html'

    def get_context_data(self,**kwargs):
        context = super(HistoryListView,self).get_context_data(**kwargs)
        context['hn5'] = History.objects.filter(region='Северо-Западный регион', type='История', century='5' ).order_by('year')
        context['cn5'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='5' ).order_by('year')
        context['hr5'] = History.objects.filter(region='Россия', type='История', century='5' ).order_by('year')
        context['cr5'] = History.objects.filter(region='Россия', type='Культура', century='5' ).order_by('year')
        context['he5'] = History.objects.filter(region='Европа', type='История', century='5' ).order_by('year')
        context['ce5'] = History.objects.filter(region='Европа', type='Культура', century='5' ).order_by('year')
        context['ha5'] = History.objects.filter(region='Азия', type='История', century='5' ).order_by('year')
        context['ca5'] = History.objects.filter(region='Азия', type='Культура', century='5' ).order_by('year')
        context['hu5'] = History.objects.filter(region='США', type='История', century='5' ).order_by('year')
        context['cu5'] = History.objects.filter(region='США', type='Культура', century='5' ).order_by('year')

        context['hn6'] = History.objects.filter(region='Северо-Западный регион', type='История', century='6' ).order_by('year')
        context['cn6'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='6' ).order_by('year')
        context['hr6'] = History.objects.filter(region='Россия', type='История', century='6' ).order_by('year')
        context['cr6'] = History.objects.filter(region='Россия', type='Культура', century='6' ).order_by('year')
        context['he6'] = History.objects.filter(region='Европа', type='История', century='6' ).order_by('year')
        context['ce6'] = History.objects.filter(region='Европа', type='Культура', century='6' ).order_by('year')
        context['ha6'] = History.objects.filter(region='Азия', type='История', century='6' ).order_by('year')
        context['ca6'] = History.objects.filter(region='Азия', type='Культура', century='6' ).order_by('year')
        context['hu6'] = History.objects.filter(region='США', type='История', century='6' ).order_by('year')
        context['cu6'] = History.objects.filter(region='США', type='Культура', century='6' ).order_by('year')

        context['hn7'] = History.objects.filter(region='Северо-Западный регион', type='История', century='7' ).order_by('year')
        context['cn7'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='7' ).order_by('year')
        context['hr7'] = History.objects.filter(region='Россия', type='История', century='7' ).order_by('year')
        context['cr7'] = History.objects.filter(region='Россия', type='Культура', century='7' ).order_by('year')
        context['he7'] = History.objects.filter(region='Европа', type='История', century='7' ).order_by('year')
        context['ce7'] = History.objects.filter(region='Европа', type='Культура', century='7' ).order_by('year')
        context['ha7'] = History.objects.filter(region='Азия', type='История', century='7' ).order_by('year')
        context['ca7'] = History.objects.filter(region='Азия', type='Культура', century='7' ).order_by('year')
        context['hu7'] = History.objects.filter(region='США', type='История', century='7' ).order_by('year')
        context['cu7'] = History.objects.filter(region='США', type='Культура', century='7' ).order_by('year')

        context['hn8'] = History.objects.filter(region='Северо-Западный регион', type='История', century='8' ).order_by('year')
        context['cn8'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='8' ).order_by('year')
        context['hr8'] = History.objects.filter(region='Россия', type='История', century='8' ).order_by('year')
        context['cr8'] = History.objects.filter(region='Россия', type='Культура', century='8' ).order_by('year')
        context['he8'] = History.objects.filter(region='Европа', type='История', century='8' ).order_by('year')
        context['ce8'] = History.objects.filter(region='Европа', type='Культура', century='8' ).order_by('year')
        context['ha8'] = History.objects.filter(region='Азия', type='История', century='8' ).order_by('year')
        context['ca8'] = History.objects.filter(region='Азия', type='Культура', century='8' ).order_by('year')
        context['hu8'] = History.objects.filter(region='США', type='История', century='8' ).order_by('year')
        context['cu8'] = History.objects.filter(region='США', type='Культура', century='8' ).order_by('year')

        context['hn9'] = History.objects.filter(region='Северо-Западный регион', type='История', century='9' ).order_by('year')
        context['cn9'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='9' ).order_by('year')
        context['hr9'] = History.objects.filter(region='Россия', type='История', century='9' ).order_by('year')
        context['cr9'] = History.objects.filter(region='Россия', type='Культура', century='9' ).order_by('year')
        context['he9'] = History.objects.filter(region='Европа', type='История', century='9' ).order_by('year')
        context['ce9'] = History.objects.filter(region='Европа', type='Культура', century='9' ).order_by('year')
        context['ha9'] = History.objects.filter(region='Азия', type='История', century='9' ).order_by('year')
        context['ca9'] = History.objects.filter(region='Азия', type='Культура', century='9' ).order_by('year')
        context['hu9'] = History.objects.filter(region='США', type='История', century='9' ).order_by('year')
        context['cu9'] = History.objects.filter(region='США', type='Культура', century='9' ).order_by('year')

        context['hn10'] = History.objects.filter(region='Северо-Западный регион', type='История', century='10' ).order_by('year')
        context['cn10'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='10' ).order_by('year')
        context['hr10'] = History.objects.filter(region='Россия', type='История', century='10' ).order_by('year')
        context['cr10'] = History.objects.filter(region='Россия', type='Культура', century='10' ).order_by('year')
        context['he10'] = History.objects.filter(region='Европа', type='История', century='10' ).order_by('year')
        context['ce10'] = History.objects.filter(region='Европа', type='Культура', century='10' ).order_by('year')
        context['ha10'] = History.objects.filter(region='Азия', type='История', century='10' ).order_by('year')
        context['ca10'] = History.objects.filter(region='Азия', type='Культура', century='10' ).order_by('year')
        context['hu10'] = History.objects.filter(region='США', type='История', century='10' ).order_by('year')
        context['cu10'] = History.objects.filter(region='США', type='Культура', century='10' ).order_by('year')

        context['hn11'] = History.objects.filter(region='Северо-Западный регион', type='История', century='11' ).order_by('year')
        context['cn11'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='11' ).order_by('year')
        context['hr11'] = History.objects.filter(region='Россия', type='История', century='11' ).order_by('year')
        context['cr11'] = History.objects.filter(region='Россия', type='Культура', century='11' ).order_by('year')
        context['he11'] = History.objects.filter(region='Европа', type='История', century='11' ).order_by('year')
        context['ce11'] = History.objects.filter(region='Европа', type='Культура', century='11' ).order_by('year')
        context['ha11'] = History.objects.filter(region='Азия', type='История', century='11' ).order_by('year')
        context['ca11'] = History.objects.filter(region='Азия', type='Культура', century='11' ).order_by('year')
        context['hu11'] = History.objects.filter(region='США', type='История', century='11' ).order_by('year')
        context['cu11'] = History.objects.filter(region='США', type='Культура', century='11' ).order_by('year')

        context['hn12'] = History.objects.filter(region='Северо-Западный регион', type='История', century='12' ).order_by('year')
        context['cn12'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='12' ).order_by('year')
        context['hr12'] = History.objects.filter(region='Россия', type='История', century='12' ).order_by('year')
        context['cr12'] = History.objects.filter(region='Россия', type='Культура', century='12' ).order_by('year')
        context['he12'] = History.objects.filter(region='Европа', type='История', century='12' ).order_by('year')
        context['ce12'] = History.objects.filter(region='Европа', type='Культура', century='12' ).order_by('year')
        context['ha12'] = History.objects.filter(region='Азия', type='История', century='12' ).order_by('year')
        context['ca12'] = History.objects.filter(region='Азия', type='Культура', century='12' ).order_by('year')
        context['hu12'] = History.objects.filter(region='США', type='История', century='12' ).order_by('year')
        context['cu12'] = History.objects.filter(region='США', type='Культура', century='12' ).order_by('year')

        context['hn13'] = History.objects.filter(region='Северо-Западный регион', type='История', century='13' ).order_by('year')
        context['cn13'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='13' ).order_by('year')
        context['hr13'] = History.objects.filter(region='Россия', type='История', century='13' ).order_by('year')
        context['cr13'] = History.objects.filter(region='Россия', type='Культура', century='13' ).order_by('year')
        context['he13'] = History.objects.filter(region='Европа', type='История', century='13' ).order_by('year')
        context['ce13'] = History.objects.filter(region='Европа', type='Культура', century='13' ).order_by('year')
        context['ha13'] = History.objects.filter(region='Азия', type='История', century='13' ).order_by('year')
        context['ca13'] = History.objects.filter(region='Азия', type='Культура', century='13' ).order_by('year')
        context['hu13'] = History.objects.filter(region='США', type='История', century='13' ).order_by('year')
        context['cu13'] = History.objects.filter(region='США', type='Культура', century='13' ).order_by('year')

        context['hn14'] = History.objects.filter(region='Северо-Западный регион', type='История', century='14' ).order_by('year')
        context['cn14'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='14' ).order_by('year')
        context['hr14'] = History.objects.filter(region='Россия', type='История', century='14' ).order_by('year')
        context['cr14'] = History.objects.filter(region='Россия', type='Культура', century='14' ).order_by('year')
        context['he14'] = History.objects.filter(region='Европа', type='История', century='14' ).order_by('year')
        context['ce14'] = History.objects.filter(region='Европа', type='Культура', century='14' ).order_by('year')
        context['ha14'] = History.objects.filter(region='Азия', type='История', century='14' ).order_by('year')
        context['ca14'] = History.objects.filter(region='Азия', type='Культура', century='14' ).order_by('year')
        context['hu14'] = History.objects.filter(region='США', type='История', century='14' ).order_by('year')
        context['cu14'] = History.objects.filter(region='США', type='Культура', century='14' ).order_by('year')

        context['hn15'] = History.objects.filter(region='Северо-Западный регион', type='История', century='15' ).order_by('year')
        context['cn15'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='15' ).order_by('year')
        context['hr15'] = History.objects.filter(region='Россия', type='История', century='15' ).order_by('year')
        context['cr15'] = History.objects.filter(region='Россия', type='Культура', century='15' ).order_by('year')
        context['he15'] = History.objects.filter(region='Европа', type='История', century='15' ).order_by('year')
        context['ce15'] = History.objects.filter(region='Европа', type='Культура', century='15' ).order_by('year')
        context['ha15'] = History.objects.filter(region='Азия', type='История', century='15' ).order_by('year')
        context['ca15'] = History.objects.filter(region='Азия', type='Культура', century='15' ).order_by('year')
        context['hu15'] = History.objects.filter(region='США', type='История', century='15' ).order_by('year')
        context['cu15'] = History.objects.filter(region='США', type='Культура', century='15' ).order_by('year')

        context['hn16'] = History.objects.filter(region='Северо-Западный регион', type='История', century='16' ).order_by('year')
        context['cn16'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='16' ).order_by('year')
        context['hr16'] = History.objects.filter(region='Россия', type='История', century='16' ).order_by('year')
        context['cr16'] = History.objects.filter(region='Россия', type='Культура', century='16' ).order_by('year')
        context['he16'] = History.objects.filter(region='Европа', type='История', century='16' ).order_by('year')
        context['ce16'] = History.objects.filter(region='Европа', type='Культура', century='16' ).order_by('year')
        context['ha16'] = History.objects.filter(region='Азия', type='История', century='16' ).order_by('year')
        context['ca16'] = History.objects.filter(region='Азия', type='Культура', century='16' ).order_by('year')
        context['hu16'] = History.objects.filter(region='США', type='История', century='16' ).order_by('year')
        context['cu16'] = History.objects.filter(region='США', type='Культура', century='16' ).order_by('year')

        context['hn17'] = History.objects.filter(region='Северо-Западный регион', type='История', century='17' ).order_by('year')
        context['cn17'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='17' ).order_by('year')
        context['hr17'] = History.objects.filter(region='Россия', type='История', century='17' ).order_by('year')
        context['cr17'] = History.objects.filter(region='Россия', type='Культура', century='17' ).order_by('year')
        context['he17'] = History.objects.filter(region='Европа', type='История', century='17' ).order_by('year')
        context['ce17'] = History.objects.filter(region='Европа', type='Культура', century='17' ).order_by('year')
        context['ha17'] = History.objects.filter(region='Азия', type='История', century='17' ).order_by('year')
        context['ca17'] = History.objects.filter(region='Азия', type='Культура', century='17' ).order_by('year')
        context['hu17'] = History.objects.filter(region='США', type='История', century='17' ).order_by('year')
        context['cu17'] = History.objects.filter(region='США', type='Культура', century='17' ).order_by('year')

        context['hn18'] = History.objects.filter(region='Северо-Западный регион', type='История', century='18' ).order_by('year')
        context['cn18'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='18' ).order_by('year')
        context['hr18'] = History.objects.filter(region='Россия', type='История', century='18' ).order_by('year')
        context['cr18'] = History.objects.filter(region='Россия', type='Культура', century='18' ).order_by('year')
        context['he18'] = History.objects.filter(region='Европа', type='История', century='18' ).order_by('year')
        context['ce18'] = History.objects.filter(region='Европа', type='Культура', century='18' ).order_by('year')
        context['ha18'] = History.objects.filter(region='Азия', type='История', century='18' ).order_by('year')
        context['ca18'] = History.objects.filter(region='Азия', type='Культура', century='18' ).order_by('year')
        context['hu18'] = History.objects.filter(region='США', type='История', century='18' ).order_by('year')
        context['cu18'] = History.objects.filter(region='США', type='Культура', century='18' ).order_by('year')

        context['hn19'] = History.objects.filter(region='Северо-Западный регион', type='История', century='19' ).order_by('year')
        context['cn19'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='19' ).order_by('year')
        context['hr19'] = History.objects.filter(region='Россия', type='История', century='19' ).order_by('year')
        context['cr19'] = History.objects.filter(region='Россия', type='Культура', century='19' ).order_by('year')
        context['he19'] = History.objects.filter(region='Европа', type='История', century='19' ).order_by('year')
        context['ce19'] = History.objects.filter(region='Европа', type='Культура', century='19' ).order_by('year')
        context['ha19'] = History.objects.filter(region='Азия', type='История', century='19' ).order_by('year')
        context['ca19'] = History.objects.filter(region='Азия', type='Культура', century='19' ).order_by('year')
        context['hu19'] = History.objects.filter(region='США', type='История', century='19' ).order_by('year')
        context['cu19'] = History.objects.filter(region='США', type='Культура', century='19' ).order_by('year')

        context['hn20'] = History.objects.filter(region='Северо-Западный регион', type='История', century='20' ).order_by('year')
        context['cn20'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='20' ).order_by('year')
        context['hr20'] = History.objects.filter(region='Россия', type='История', century='20' ).order_by('year')
        context['cr20'] = History.objects.filter(region='Россия', type='Культура', century='20' ).order_by('year')
        context['he20'] = History.objects.filter(region='Европа', type='История', century='20' ).order_by('year')
        context['ce20'] = History.objects.filter(region='Европа', type='Культура', century='20' ).order_by('year')
        context['ha20'] = History.objects.filter(region='Азия', type='История', century='20' ).order_by('year')
        context['ca20'] = History.objects.filter(region='Азия', type='Культура', century='20' ).order_by('year')
        context['hu20'] = History.objects.filter(region='США', type='История', century='20' ).order_by('year')
        context['cu20'] = History.objects.filter(region='США', type='Культура', century='20' ).order_by('year')

        context['hn21'] = History.objects.filter(region='Северо-Западный регион', type='История', century='21' ).order_by('year')
        context['cn21'] = History.objects.filter(region='Северо-Западный регион', type='Культура', century='21' ).order_by('year')
        context['hr21'] = History.objects.filter(region='Россия', type='История', century='21' ).order_by('year')
        context['cr21'] = History.objects.filter(region='Россия', type='Культура', century='21' ).order_by('year')
        context['he21'] = History.objects.filter(region='Европа', type='История', century='21' ).order_by('year')
        context['ce21'] = History.objects.filter(region='Европа', type='Культура', century='21' ).order_by('year')
        context['ha21'] = History.objects.filter(region='Азия', type='История', century='21' ).order_by('year')
        context['ca21'] = History.objects.filter(region='Азия', type='Культура', century='21' ).order_by('year')
        context['hu21'] = History.objects.filter(region='США', type='История', century='20' ).order_by('year')
        context['cu21'] = History.objects.filter(region='США', type='Культура', century='21' ).order_by('year')


        return context

class HistoryStrView(TemplateView):
    """ выводит отдельное историческое событие """
    model = History
    template_name = 'hike/historystr.html'


    def get_object(self, queryset=None):
        return History.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(HistoryStrView, self).get_context_data(**kwargs)
        obj = History.objects.get(pk=self.kwargs.get("pk"))
        context['obj'] = obj

        return context

from django.views.generic import ListView
from django.db.models import Q
from django.utils import timezone
from .models import Hike, RouteFeature
from .forms import SearchForm

class HikeAllListView(ListView):
    """
    Класс выводит список всех маршрутов походов,
    обрабатывает текстовый поиск и поддерживает любую 
    комбинацию пяти фильтров одновременно без сброса состояния.
    """
    model = Hike
    template_name = 'hike/mainlist.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6

    def get_queryset(self):
        # Базовый QuerySet со всеми маршрутами
        queryset = super().get_queryset()

        # 1. Текстовый поиск (Searchword)
        searchword = self.request.GET.get('searchword', '').strip()
        if searchword:
            # Делаем первую букву заглавной для поддержки вашего алгоритма
            searchword1 = searchword[0].upper() + searchword[1:] if len(searchword) > 0 else searchword
            queryset = queryset.filter(
                Q(title__icontains=searchword) | Q(title__icontains=searchword1) |
                Q(country__icontains=searchword) | Q(country__icontains=searchword1) |
                Q(region__icontains=searchword) | Q(region__icontains=searchword1) |
                Q(start_station__icontains=searchword) | Q(start_station__icontains=searchword1) |
                Q(aim_station__icontains=searchword) | Q(aim_station__icontains=searchword1) |
                Q(home_station__icontains=searchword) | Q(home_station__icontains=searchword1) |
                Q(back_station__icontains=searchword) | Q(back_station__icontains=searchword1) |
                Q(travel_details__icontains=searchword) | Q(travel_details__icontains=searchword1) |
                Q(attractions__icontains=searchword) | Q(attractions__icontains=searchword1)
            ).distinct()

        # 2. Фильтр: Пройдено в этом году (pk)
        pk = self.request.GET.get('pk', '0')
        if pk.isdigit():
            pk = int(pk)
            if pk == 1:
                ar = str(timezone.now().year)[2:]
                arr = f'{ar};'
                queryset = queryset.filter(Q(dates_try__iendswith=ar) | Q(dates_try__iendswith=arr))
            elif pk == 2:
                ar = str(timezone.now().year)[2:]
                arr = f'{ar};'
                queryset = queryset.exclude(Q(dates_try__iendswith=ar) | Q(dates_try__iendswith=arr))

        # 3. Фильтр: Пройдено когда-то вообще (qk)
        qk = self.request.GET.get('qk', '0')
        if qk.isdigit():
            qk = int(qk)
            if qk == 1:
                queryset = queryset.filter(reality=True)
            elif qk == 2:
                queryset = queryset.filter(reality=False)

        # 4. Фильтр: Готовность маршрута (rk)
        rk = self.request.GET.get('rk', '0')
        if rk.isdigit():
            rk = int(rk)
            if rk == 1:
                queryset = queryset.filter(maturity=True)
            elif rk == 2:
                queryset = queryset.filter(maturity=False)

        # 5. Фильтр: Особенности маршрута (fk)
        fk = self.request.GET.get('fk', '0')
        if fk.isdigit():
            fk = int(fk)
            if fk > 0:
                queryset = queryset.filter(features__pk=fk)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Безопасно получаем и сохраняем текущие значения фильтров в контекст шаблона
        def get_int_param(param_name):
            val = self.request.GET.get(param_name, '0')
            return int(val) if val.isdigit() else 0

        context['pk'] = get_int_param('pk')
        context['qk'] = get_int_param('qk')
        context['rk'] = get_int_param('rk')
        context['fk'] = get_int_param('fk')
        
        # Возвращаем поисковую фразу обратно в форму для красивого отображения
        searchword = self.request.GET.get('searchword', '')
        context['form'] = SearchForm(initial={'searchword': searchword})
        
        # Передаем полный список динамических особенностей для выпадающего меню
        context['all_features'] = RouteFeature.objects.all()
        
        # Формируем и сохраняем строку активных GET-фильтров.
        # Это нужно, чтобы при клике на пагинацию (следующая страница) фильтры не сбрасывались.
        current_params = self.request.GET.copy()
        if 'page' in current_params:
            del current_params['page']
        context['current_filters_url'] = f"&{current_params.urlencode()}" if current_params else ""
        
        return context




