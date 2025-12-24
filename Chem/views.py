import random

from django.views.generic import ListView, TemplateView, View
from django.shortcuts import render, redirect
from django.db.models import Q

from Chem.models import *



from .models import *
from .forms import *




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
    """ выводит заглавную страницу теста по неорганической химии для конкретного закона неорганической химии """
    """path('inorganiclaw/test/<str:str>/', views.ChemTestHeadView.as_view(), name='inorganiclawtest'),"""
    
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(ChemTestHeadView, self).get_context_data(**kwargs)
        str=self.kwargs['str']
        
        try:
            a = InorganicReaction.objects.filter(number__pk=str).first()
            c = InorganicReaction.objects.filter(number__pk=str)
            context['numbertitle'] = a.number.title
            context['count'] = InorganicReaction.objects.filter(number__pk=str).count()
            question_ids = list(c.values_list('id', flat=True))
            random.shuffle(question_ids)
            context['q1'] = InorganicReaction.objects.get(pk=question_ids[0]).pk            
            question_ids.pop(0)
            context['question_ids'] = question_ids           
            self.request.session['question_list'] = question_ids


        except:
            context['numbertitle'] = 'Пока нет реакций'
            context['count'] = ''
            context['question_ids'] = '' 
            context['q1'] = 0
        return context

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = InorganicReaction.objects.filter(number__pk=str)
        return queryset


class ChemTestQuestionView(TemplateView):
    template_name = 'Chem/inorganiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        # Вызываем базовый метод для получения контекста
        context = super().get_context_data(**kwargs)
        str=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        
        # Добавляем данные в контекст шаблона
        context['reagent1'] = InorganicReaction.objects.get(pk=str).reagent1
        context['reagent2'] = InorganicReaction.objects.get(pk=str).reagent2
        context['reagent3'] = InorganicReaction.objects.get(pk=str).reagent3
        context['condition'] = InorganicReaction.objects.get(pk=str).condition
        context['form']= Unswer4Form

        context['q1'] = str
        
        context['items'] = my_data
        context['count'] = len(my_data)
        
        return context


    def post(self, request, *args, **kwargs):
        # Получение данных из POST-запроса
        product1 = request.POST.get('product1')
        product2 = request.POST.get('product2')
        product3 = request.POST.get('product3')
        product4 = request.POST.get('product4')
        self.request.session['answer_list'] = [product1, product2, product3, product4]
        return redirect('inorganiclawtestanswer', str=6)
        


class ChemTestAnswerView(TemplateView):
    template_name = 'Chem/inorganiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        # Вызываем базовый метод для получения контекста
        context = super().get_context_data(**kwargs)
        str=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        my_answer = self.request.session.get('answer_list', [])
        
        # Добавляем данные в контекст шаблона
        context['reagent1'] = InorganicReaction.objects.get(pk=str).reagent1
        context['reagent2'] = InorganicReaction.objects.get(pk=str).reagent2
        context['reagent3'] = InorganicReaction.objects.get(pk=str).reagent3
        context['condition'] = InorganicReaction.objects.get(pk=str).condition
        context['product1'] = InorganicReaction.objects.get(pk=str).product1
        context['product2'] = InorganicReaction.objects.get(pk=str).product2
        context['product3'] = InorganicReaction.objects.get(pk=str).product3
        context['product4'] = InorganicReaction.objects.get(pk=str).product4

        context['q1'] = str

        context['my_answer'] = my_answer

        context['items'] = my_data
        context['count'] = len(my_data)
        
        return context
