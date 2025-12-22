from django.views.generic import ListView, TemplateView, View
from django.shortcuts import render, redirect
from django.db.models import Q

from Chem.models import *


from django import forms
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class SearchForm(forms.Form):
    """форма для поиска по полям модели"""
    searchword = forms.CharField(label='Поиск', required=False,
                           help_text='слово для поиска',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('searchword', css_class='form-group col-md-10 mb-0'),
                Row(Submit('submit', 'Найти', css_class='btn  btn-warning col-md-9 mb-3 mt-4 ml-4'))))



class ChemView(View):
    """выводит страницу химия"""
    def get(self, request):
        return render(request, 'Chem/chem.html')


class InorganiclawView(ListView):
    """ Выводит список всех постов """
    model = Inorganiclaw
    template_name = 'Chem/inorganiclaw.html'
    context_object_name = 'objects'
    ordering = ['number']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(InorganiclawView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class InorganiclawStrView(TemplateView):
    """ выводит отдельный пост """
    model = Inorganiclaw
    template_name = 'Chem/inorganiclawstr.html'


    def get_object(self, queryset=None):
        return Inorganiclaw.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(InorganiclawStrView, self).get_context_data(**kwargs)
        obj = Inorganiclaw.objects.get(pk=self.kwargs.get("pk"))
        context['obj'] = obj
        return context



class ChemSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по законам химии """

    template_name = 'Chem/inorganiclaw.html'

    def get_context_data(self, **kwargs):
        context = super(ChemSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Inorganiclaw.objects.\
            filter(Q(keywords__icontains=searchword)|Q(keywords__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context

class ChemTestHeadView(ListView):
    """ выводит заглавную страницу теста по неорганической химии для конкретного вопроса """
    """path('inorganiclaw/test/<str:str>/', views.ChemTestHeadView.as_view(), name='inorganiclawtest'),"""
    
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(ChemTestHeadView, self).get_context_data(**kwargs)
        str=self.kwargs['str']
        a = InorganicReaction.objects.filter(number__pk=str).first()
        context['numbertitle'] = a.title
        context['count'] = InorganicReaction.objects.filter(number__pk=str).count()
      
        return context

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = InorganicReaction.objects.filter(number__pk=str)
        return queryset
