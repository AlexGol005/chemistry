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
        ind=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        qw = InorganicReaction.objects.get(pk=ind)
        
        # Добавляем данные в контекст шаблона
        context['reagent1'] = qw.reagent1
        context['reagent2'] = qw.reagent2
        context['reagent3'] = qw.reagent3
        context['condition'] = qw.condition
        context['form']= Unswer4Form

        context['q1'] = ind
        
        context['items'] = my_data
        context['count'] = len(my_data)
        
        return context


    def post(self, request, *args, **kwargs):
        # Получение данных из POST-запроса
        ind=self.kwargs['str']
        ind=int(ind)
        qw = InorganicReaction.objects.get(pk=ind)
        product1 = request.POST.get('field1')
        product2 = request.POST.get('field2')
        product3 = request.POST.get('field3')
        product4 = request.POST.get('field4')
        answer_list = [product1, product2, product3, product4]
        answer_list_upper = [word.upper() for word in answer_list]
        correct_answer_list = [qw.product1, qw.product2, qw.product3, qw.product4]
        correct_answer_list_upper = [word.upper() for word in correct_answer_list]
        clean_answer_list_upper = list(filter(None, answer_list_upper))
        clean_correct_answer_list_upper = list(filter(None, correct_answer_list_upper))
        if sorted(clean_answer_list_upper) == sorted(correct_answer_list_upper):
            messages.success(request, "Верно!")
        else:
            messages.success(request, "Не верно :(")
        
        self.request.session['answer_list'] = answer_list
        return redirect('inorganiclawtestanswer', str=ind)
        


class ChemTestAnswerView(TemplateView):
    template_name = 'Chem/inorganiclawtestanswer.html'

    def get_context_data(self, **kwargs):

        # вывод ответа
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        context['reagent1'] = InorganicReaction.objects.get(pk=ind).reagent1
        context['reagent2'] = InorganicReaction.objects.get(pk=ind).reagent2
        context['reagent3'] = InorganicReaction.objects.get(pk=ind).reagent3
        context['condition'] = InorganicReaction.objects.get(pk=ind).condition
        context['product1'] = InorganicReaction.objects.get(pk=ind).product1
        context['product2'] = InorganicReaction.objects.get(pk=ind).product2
        context['product3'] = InorganicReaction.objects.get(pk=ind).product3
        context['product4'] = InorganicReaction.objects.get(pk=ind).product4
        

        # проверка ответа
        my_answer = self.request.session.get('answer_list', [])
        context['my_answer'] = my_answer

        # поиск следующего уравнения через индекс из списка (список сначала запомним потом перезапишем)
        last_list = self.request.session.get('question_list', [])
        
        question_list = self.request.session.get('question_list', [])
        try:
            next_index =  question_list.pop(0)
        except:
            next_index = None
            
        self.request.session['question_list'] = question_list

        question_list = self.request.session.get('question_list', [])
        
        
        context['next_index'] = next_index
       
        context['items'] = question_list
        context['count'] = len(question_list)
        context['last_list'] = last_list
        
        return context
