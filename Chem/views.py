import random
from django.contrib import messages
from django.views.generic import ListView, TemplateView, View, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import *
from rdkit import Chem as Chemredactor

class OrganicNamesTestStartView(View):
    def get(self, request):
        ids = list(OrganicNames.objects.values_list('id', flat=True))
        random.shuffle(ids)
        request.session['organicnamestest_ids'] = ids
        request.session['organicnamestest_score'] = 0  # Обнуляем счетчик в начале
        return render(request, 'Chem/organicnamestest_start.html')

class OrganicNamesTestQuestionView(View):
    def get(self, request, index):
        test_ids = request.session.get('organicnamestest_ids', [])
        
        if not test_ids or index >= len(test_ids):
            # Если вопросы закончились, можно перенаправить на начало или спец. страницу
            return render(request, 'Chem/organicnamestest_finished.html')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        return render(request, 'Chem/organicnamestest_question.html', {
            'molecule': obj, # Передаем объект как 'molecule'
            'index': index
        })



class OrganicNamesTestAnswerView(View):
    def post(self, request, index):
        user_smiles = request.POST.get('user_smiles', '')
        test_ids = request.session.get('organicnamestest_ids', [])
        
        if not test_ids or index >= len(test_ids):
            return redirect('organicnamestest_start')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        ref_smiles = obj.molecule  
        
        is_correct = False
        mol_user = Chemredactor.MolFromSmiles(user_smiles)
        mol_ref = Chemredactor.MolFromSmiles(ref_smiles) if ref_smiles else None
        
        if mol_user and mol_ref:
            user_can = Chemredactor.MolToSmiles(mol_user, isomericSmiles=True)
            ref_can = Chemredactor.MolToSmiles(mol_ref, isomericSmiles=True)
            is_correct = (user_can == ref_can)
            
            # Увеличиваем счетчик в сессии, если ответ верный
            if is_correct:
                request.session['organicnamestest_score'] = request.session.get('organicnamestest_score', 0) + 1
        
        return render(request, 'Chem/organicnamestest_answer.html', {
            'molecule': obj,
            'user_smiles': user_smiles,
            'is_correct': is_correct,
            'next_index': index + 1,
            'total_questions': len(test_ids) # Передаем общее количество для условий
        })

class OrganicNamesTestFinishedView(View):
    def get(self, request):
        score = request.session.get('organicnamestest_score', 0)
        test_ids = request.session.get('organicnamestest_ids', [])
        total = len(test_ids)
        
        context = {
            'score': score,
            'total': total,
            # Можно добавить процент успеха
            'percent': int((score / total) * 100) if total > 0 else 0
        }
        return render(request, 'Chem/organicnamestest_finished.html', context)




# начало
class ChemView(View):
    """выводит страницу химия"""
    def get(self, request):
        return render(request, 'Chem/chem.html')

class TablesView(ListView):
    """ Выводит все таблицы """
    model = Table
    template_name = 'Chem/tables.html'
    context_object_name = 'objects'
    ordering = ['pk']

class LinkView(ListView):
    """ Выводит все ссылки """
    model = Link
    template_name = 'Chem/link.html'
    context_object_name = 'objects'
    ordering = ['pk']


class InorganiclawView(ListView):
    """ Выводит список всех всех законов неорганической химии """
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
    """ выводит отдельный закон неорганической химии """
    model = Inorganiclaw
    template_name = 'Chem/inorganiclawstr.html'


    def get_object(self, queryset=None):
        return Inorganiclaw.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(InorganiclawStrView, self).get_context_data(**kwargs)
        obj = Inorganiclaw.objects.get(pk=self.kwargs.get("pk"))
        qw = InorganicReaction.objects.filter(number=obj)
        context['obj'] = obj
        context['qw'] = qw
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
            filter(Q(keywords__icontains=searchword)|Q(keywords__icontains=searchword1)|Q(title__icontains=searchword)|Q(title__icontains=searchword1)).order_by('pk')
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
            self.request.session['correct_count'] = 0
            self.request.session['incorrect_count'] = 0
            self.request.session['all_count'] = 0
            



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


class ChemMyTestHeadView(ListView):
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_queryset(self):
        # Получаем только те реакции, которые есть в списке текущего юзера
        return InorganicReaction.objects.filter(
            userreaction__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        if queryset.exists():
            # Заголовок теперь логичнее сделать общим, так как это "Мой список"
            context['numbertitle'] = "Мои сохраненные реакции"
            context['count'] = queryset.count()
            
            # Работа с ID для теста
            question_ids = list(queryset.values_list('id', flat=True))
            random.shuffle(question_ids)
            
            q1_id = question_ids.pop(0)
            context['q1'] = q1_id
            
            # Обновляем сессию
            context['question_ids'] = question_ids           
            self.request.session['question_list'] = question_ids
            self.request.session['correct_count'] = 0
            self.request.session['incorrect_count'] = 0
            self.request.session['all_count'] = 0
        else:
            context['numbertitle'] = 'В вашем списке пока нет реакций'
            context['count'] = 0
            context['q1'] = 0
            
        return context





class ChemTestQuestionView(TemplateView):
    """ выводит вопрос теста - реакцию  по неорганической химии """
    template_name = 'Chem/inorganiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        # Вызываем базовый метод для получения контекста
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        qw = InorganicReaction.objects.get(pk=ind)
        
        name1 = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('name', flat=True).first() or ""
        name2 = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('name', flat=True).first() or ""
        name3 = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('name', flat=True).first() or ""
        context['name1'] = name1
        context['name2'] = name2
        context['name3'] = name3
        
        # Добавляем данные в контекст шаблона
        context['reagent1'] = qw.reagent1
        context['reagent2'] = qw.reagent2
        context['reagent3'] = qw.reagent3

        context['condition'] = qw.condition
        context['form']= Unswer4Form

        context['q1'] = ind
        context['obj'] = qw
        
        context['items'] = my_data
        context['count'] = len(my_data)
        self.request.session['all_count'] += 1 
        
        return context


    def post(self, request, *args, **kwargs):
        # Получение данных из POST-запроса
        ind=self.kwargs['str']
        ind=int(ind)
        qw = InorganicReaction.objects.get(pk=ind)
        product1 = request.POST.get('field1')
        if product1 == "not":
            product1 = "нет"
        if product1 == "ytn":
            product1 = "нет"
        if product1 == "Ytn":
            product1 = "нет"
        if product1 == "Not":
            product1 = "нет"
        if product1 == "Нет":
            product1 = "нет"
        product2 = request.POST.get('field2')
        product3 = request.POST.get('field3')
        product4 = request.POST.get('field4')
        answer_list = [product1, product2, product3, product4]
        correct_answer_list = [qw.product1, qw.product2, qw.product3, qw.product4]

        clean_answer_list = list(filter(None, answer_list))
        clean_correct_answer_list = list(filter(None, correct_answer_list))
        
        clean_answer_list_upper = [word.upper() for word in clean_answer_list]
        
        clean_correct_answer_list_upper = [word.upper() for word in clean_correct_answer_list]
        answer = " + ".join(clean_answer_list)

        if sorted(clean_answer_list_upper) == sorted(clean_correct_answer_list_upper) and sorted(clean_correct_answer_list_upper) != []:
            messages.success(request, "Верно!")
            self.request.session['correct_count'] += 1

        elif sorted(clean_answer_list_upper) == sorted(clean_correct_answer_list_upper) and sorted(clean_correct_answer_list_upper) == []:
            messages.success(request, "нет ответа")
            self.request.session['correct_count'] += 1
            
        else:
            messages.success(request, f'Не верно :( .Ваш ответ: = {answer}')
            self.request.session['incorrect_count'] += 1
            
        
        # self.request.session['all_count'] += 1 
        
        self.request.session['answer_list'] = answer_list
        return redirect('inorganiclawtestanswer', str=ind)
        


class ChemTestAnswerView(TemplateView):
    """ выводит ответ теста - реакцию  по неорганической химии """
    
    template_name = 'Chem/inorganiclawtestanswer.html'

    def get_context_data(self, **kwargs):

        # вывод ответа
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        qw = InorganicReaction.objects.get(pk=ind)
        context['reagent1'] = InorganicReaction.objects.get(pk=ind).reagent1
        context['reagent2'] = InorganicReaction.objects.get(pk=ind).reagent2
        context['reagent3'] = InorganicReaction.objects.get(pk=ind).reagent3
        context['condition'] = InorganicReaction.objects.get(pk=ind).condition
        context['product1'] = InorganicReaction.objects.get(pk=ind).product1
        context['product2'] = InorganicReaction.objects.get(pk=ind).product2
        context['product3'] = InorganicReaction.objects.get(pk=ind).product3
        context['product4'] = InorganicReaction.objects.get(pk=ind).product4


        
        name1 = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('name', flat=True).first() or ""
        name2 = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('name', flat=True).first() or ""
        name3 = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('name', flat=True).first() or ""
        context['name1'] = name1
        context['name2'] = name2
        context['name3'] = name3

        pkc1 = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('pk', flat=True).first() or ""
        pkc2 = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('pk', flat=True).first() or ""
        pkc3 = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('pk', flat=True).first() or ""

        
        name4 = NamesCompaunds.objects.filter(formula=qw.product1).values_list('name', flat=True).first() or ""
        name5 = NamesCompaunds.objects.filter(formula=qw.product2).values_list('name', flat=True).first() or ""
        name6 = NamesCompaunds.objects.filter(formula=qw.product3).values_list('name', flat=True).first() or ""
        name7 = NamesCompaunds.objects.filter(formula=qw.product4).values_list('name', flat=True).first() or ""
        context['name4'] = name4
        context['name5'] = name5
        context['name6'] = name6
        context['name7'] = name7

        pkc4 = NamesCompaunds.objects.filter(formula=qw.product1).values_list('pk', flat=True).first() or ""
        pkc5 = NamesCompaunds.objects.filter(formula=qw.product2).values_list('pk', flat=True).first() or ""
        pkc6 = NamesCompaunds.objects.filter(formula=qw.product3).values_list('pk', flat=True).first() or ""
        pkc7 = NamesCompaunds.objects.filter(formula=qw.product4).values_list('pk', flat=True).first() or ""

        my_list = [pkc1, pkc2, pkc3, pkc4, pkc5, pkc6, pkc7]
        new_list = [x if x != "" else 1 for x in my_list]

        context['pkc1'] = new_list[0]
        context['pkc2'] = new_list[1]
        context['pkc3'] = new_list[2]
        context['pkc4'] = new_list[3]
        context['pkc5'] = new_list[4]
        context['pkc6'] = new_list[5]
        context['pkc7'] = new_list[6]


        
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

        correct_count = self.request.session.get('correct_count')
        incorrect_count = self.request.session.get('incorrect_count')
        all_count = self.request.session.get('all_count')
        if all_count == 0:
            percent = 0
        else:
            
            percent = round((correct_count / all_count) * 100)

        
        
        context['next_index'] = next_index
       
        context['items'] = question_list
        context['count'] = len(question_list)
        context['last_list'] = last_list
        context['obj'] = qw
        context['percent'] = percent

        # блок добавки реакций в список любимых авторизованного пользователя
    
        if self.request.user.is_authenticated:
        # Получаем плоский список ID реакций, которые добавил этот пользователь
            context['favorite_ids'] = list(UserReaction.objects.filter(
                user=self.request.user
            ).values_list('reaction_id', flat=True))
        else:
            context['favorite_ids'] = []
        
        return context


class CompaundStrView(TemplateView):
    """страница химического вещества"""
    template_name = 'Chem/compaund.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        objcontent = NamesCompaunds.objects.get(pk=ind) 
        f = objcontent.formula
        context['objcontent'] = objcontent

        qw = InorganicReaction.objects.filter(Q(reagent1__icontains=f) | Q(reagent2__icontains=f) | Q(reagent3__icontains=f) | Q(product1__icontains=f) | Q(product2__icontains=f) | Q(product3__icontains=f) | Q(product4__icontains=f) )

        context['qw'] = qw
        
        return context


class AtomlawView(ListView):
    """ Выводит список всех всех законов общей химии """
    model = Atomlaw
    template_name = 'Chem/atomlaws.html'
    context_object_name = 'objects'
    ordering = ['number']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(AtomlawView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class AtomlawStrView(TemplateView):
    """ выводит отдельный закон общей химии """
    model = Atomlaw
    template_name = 'Chem/atomlawstr.html'


    def get_object(self, queryset=None):
        return Atomlaw.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(AtomlawStrView, self).get_context_data(**kwargs)
        obj = Atomlaw.objects.get(pk=self.kwargs.get("pk"))
        qw = AtomTest.objects.filter(number=obj)
        context['obj'] = obj
        context['qw'] = qw
        return context


class AtomlawSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по законам общей химии """

    template_name = 'Chem/atomlaws.html'

    def get_context_data(self, **kwargs):
        context = super(AtomlawSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Atomlaw.objects.\
            filter(Q(keywords__icontains=searchword)|Q(keywords__icontains=searchword1)|Q(title__icontains=searchword)|Q(title__icontains=searchword1)|Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context


class AtomTestAnswerView(TemplateView):
    """ выводит ответ теста - по общей химии """
    
    template_name = 'Chem/atomlawtestanswer.html'

    def get_context_data(self, **kwargs):

        # вывод ответа
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        qw = AtomTest.objects.get(pk=ind)
  
  
        # поиск следующего вопроса через индекс из списка (список сначала запомним потом перезапишем)
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
        context['obj'] = qw 
        
        return context



class CompaundView(ListView):
    """ Выводит список всех всех веществ """
    model = NamesCompaunds
    template_name = 'Chem/compaunds.html'
    context_object_name = 'objects'
    ordering = ['pk']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(CompaundView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context



class CompaundSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по веществам """

    template_name = 'Chem/compaunds.html'

    def get_context_data(self, **kwargs):
        context = super(CompaundSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = NamesCompaunds.objects.\
            filter(Q(name__icontains=searchword)|Q(name__icontains=searchword1)|Q(formula__icontains=searchword)|Q(formula__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context






class AtomTestHeadView(ListView):
    """ выводит заглавную страницу теста по общей химии для конкретного закона общей химии """

    
    template_name = 'Chem/atomlawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(AtomTestHeadView, self).get_context_data(**kwargs)
        str=self.kwargs['str']
        
        try:
            a = AtomTest.objects.filter(number__pk=str).first()
            c = AtomTest.objects.filter(number__pk=str)
            context['numbertitle'] = a.number.title
            context['count'] = AtomTest.objects.filter(number__pk=str).count()
            question_ids = list(c.values_list('id', flat=True))
            random.shuffle(question_ids)
            context['q1'] = AtomTest.objects.get(pk=question_ids[0]).pk            
            question_ids.pop(0)
            context['question_ids'] = question_ids           
            self.request.session['question_list'] = question_ids
            self.request.session['correct_count'] = 0
            self.request.session['incorrect_count'] = 0
            self.request.session['all_count'] = 0
            



        except:
            context['numbertitle'] = 'Пока нет вопросов'
            context['count'] = ''
            context['question_ids'] = '' 
            context['q1'] = 0
        return context

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = AtomTest.objects.filter(number__pk=str)
        return queryset




class AtomTestQuestionView(TemplateView):
    """ выводит вопрос теста - законы общей химии """
    template_name = 'Chem/atomlawtestquestion.html'

    def get_context_data(self, **kwargs):
        # Вызываем базовый метод для получения контекста
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        qw = AtomTest.objects.get(pk=ind)
        
   
        context['form']= Unswer4Form

        context['q1'] = ind
        context['obj'] = qw
        
        context['items'] = my_data
        context['count'] = len(my_data)
        self.request.session['all_count'] += 1 
        
        return context


    def post(self, request, *args, **kwargs):
        # Получение данных из POST-запроса
        ind=self.kwargs['str']
        ind=int(ind)
        qw = AtomTest.objects.get(pk=ind)
 


        return redirect('atomlawtestanswer', str=ind)

def add_to_list(request, reaction_id):
    if request.method == 'POST':
        reaction = get_object_or_404(InorganicReaction, id=reaction_id)
        # get_or_create гарантирует отсутствие дублей (UniqueTogether)
        UserReaction.objects.get_or_create(user=request.user, reaction=reaction)
    
    # Возвращаем пользователя обратно
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def my_favorites_view(request):
    # Получаем все объекты UserReaction для текущего пользователя
    # select_related('reaction') подтянет данные о самих реакциях одним запросом
    user_items = UserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'my_list.html', {'user_items': user_items})

def remove_reaction(request, reaction_id):
    if request.method == 'POST':
        # Находим и удаляем связь текущего пользователя с этой реакцией
        UserReaction.objects.filter(user=request.user, reaction_id=reaction_id).delete()

    # Возвращаем пользователя туда, откуда он пришел
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def my_reactions_list(request):
    # Получаем все связи текущего пользователя с реакциями
    # select_related('reaction') подгрузит данные InorganicReaction одним запросом
    user_items = UserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'Chem/my_reactions.html', {'user_items': user_items})


# органика

class OrganiclawView(ListView):
    """ Выводит список всех всех законов органической химии """
    model = Organiclaw
    template_name = 'Chem/organiclaw.html'
    context_object_name = 'objects'
    ordering = ['number']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(OrganiclawView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class OrganiclawStrView(TemplateView):
    """ выводит отдельный закон органической химии """
    model = Organiclaw
    template_name = 'Chem/organiclawstr.html'


    def get_object(self, queryset=None):
        return Organiclaw.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(OrganiclawStrView, self).get_context_data(**kwargs)
        obj = Organiclaw.objects.get(pk=self.kwargs.get("pk"))
        qw = OrganicReaction.objects.filter(number=obj)
        context['obj'] = obj
        context['qw'] = qw
        return context


class OrganicChemSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по законам органической химии """

    template_name = 'Chem/organiclaw.html'

    def get_context_data(self, **kwargs):
        context = super(OrganicChemSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Organiclaw.objects.\
            filter(Q(keywords__icontains=searchword)|Q(keywords__icontains=searchword1)|Q(title__icontains=searchword)|Q(title__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context


class OrganicChemTestHeadView(ListView):
    """ выводит заглавную страницу теста по органической химии для конкретного закона органической химии """
    
    template_name = 'Chem/organiclawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(OrganicChemTestHeadView, self).get_context_data(**kwargs)
        str=self.kwargs['str']
        
        try:
            a = organicReaction.objects.filter(number__pk=str).first()
            c = organicReaction.objects.filter(number__pk=str)
            context['numbertitle'] = a.number.title
            context['count'] = OrganicReaction.objects.filter(number__pk=str).count()
            question_ids = list(c.values_list('id', flat=True))
            random.shuffle(question_ids)
            context['q1'] = OrganicReaction.objects.get(pk=question_ids[0]).pk            
            question_ids.pop(0)
            context['question_ids'] = question_ids           
            self.request.session['question_list'] = question_ids
            self.request.session['correct_count'] = 0
            self.request.session['incorrect_count'] = 0
            self.request.session['all_count'] = 0
            



        except:
            context['numbertitle'] = 'Пока нет реакций'
            context['count'] = ''
            context['question_ids'] = '' 
            context['q1'] = 0
        return context

    def get_queryset(self):
        str=self.kwargs['str']
        queryset = OrganicReaction.objects.filter(number__pk=str)
        return queryset


class OrganicChemMyTestHeadView(ListView):
    template_name = 'Chem/organiclawtesthead.html'
    context_object_name = 'objects'

    def get_queryset(self):
        # Получаем только те реакции, которые есть в списке текущего юзера
        return OrganicReaction.objects.filter(
            organic_userreaction__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        if queryset.exists():
            # Заголовок теперь логичнее сделать общим, так как это "Мой список"
            context['numbertitle'] = "Мои сохраненные реакции"
            context['count'] = queryset.count()
            
            # Работа с ID для теста
            question_ids = list(queryset.values_list('id', flat=True))
            random.shuffle(question_ids)
            
            q1_id = question_ids.pop(0)
            context['q1'] = q1_id
            
            # Обновляем сессию
            context['question_ids'] = question_ids           
            self.request.session['question_list'] = question_ids
            self.request.session['correct_count'] = 0
            self.request.session['incorrect_count'] = 0
            self.request.session['all_count'] = 0
        else:
            context['numbertitle'] = 'В вашем списке пока нет реакций'
            context['count'] = 0
            context['q1'] = 0
            
        return context





class OrganicChemTestQuestionView(TemplateView):
    """ выводит вопрос теста - реакцию  по неорганической химии """
    template_name = 'Chem/organiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        # Вызываем базовый метод для получения контекста
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']

        # Получаем данные из сессии по ключу 'my_list'
        # Если ключа нет, вернется пустой список []
        my_data = self.request.session.get('question_list', [])
        qw = OrganicReaction.objects.get(pk=ind)
        
        name1 = OrganicNames.objects.filter(name1=qw.reagent1).values_list('name1', flat=True).first() or ""
        name2 = OrganicNames.objects.filter(name1=qw.reagent2).values_list('name1', flat=True).first() or ""
        name3 = OrganicNames.objects.filter(name1=qw.reagent3).values_list('name1', flat=True).first() or ""
        context['name1'] = name1
        context['name2'] = name2
        context['name3'] = name3
        
        # Добавляем данные в контекст шаблона
        context['reagent1'] = qw.reagent1
        context['reagent2'] = qw.reagent2
        context['reagent3'] = qw.reagent3

        context['condition'] = qw.condition
        context['form']= Unswer4Form

        context['q1'] = ind
        context['obj'] = qw
        
        context['items'] = my_data
        context['count'] = len(my_data)
        self.request.session['all_count'] += 1 
        
        return context


    def post(self, request, *args, **kwargs):
        # Получение данных из POST-запроса
        ind=self.kwargs['str']
        ind=int(ind)
        qw = OrganicReaction.objects.get(pk=ind)
        product1 = request.POST.get('field1')
        if product1 == "not":
            product1 = "нет"
        if product1 == "ytn":
            product1 = "нет"
        if product1 == "Ytn":
            product1 = "нет"
        if product1 == "Not":
            product1 = "нет"
        if product1 == "Нет":
            product1 = "нет"
        product2 = request.POST.get('field2')
        product3 = request.POST.get('field3')
        product4 = request.POST.get('field4')
        answer_list = [product1, product2, product3, product4]
        correct_answer_list = [qw.product1, qw.product2, qw.product3, qw.product4]

        clean_answer_list = list(filter(None, answer_list))
        clean_correct_answer_list = list(filter(None, correct_answer_list))
        
        clean_answer_list_upper = [word.upper() for word in clean_answer_list]
        
        clean_correct_answer_list_upper = [word.upper() for word in clean_correct_answer_list]
        answer = " + ".join(clean_answer_list)

        if sorted(clean_answer_list_upper) == sorted(clean_correct_answer_list_upper) and sorted(clean_correct_answer_list_upper) != []:
            messages.success(request, "Верно!")
            self.request.session['correct_count'] += 1

        elif sorted(clean_answer_list_upper) == sorted(clean_correct_answer_list_upper) and sorted(clean_correct_answer_list_upper) == []:
            messages.success(request, "нет ответа")
            self.request.session['correct_count'] += 1
            
        else:
            messages.success(request, f'Не верно :( .Ваш ответ: = {answer}')
            self.request.session['incorrect_count'] += 1
            
        
        # self.request.session['all_count'] += 1 
        
        self.request.session['answer_list'] = answer_list
        return redirect('inorganiclawtestanswer', str=ind)
        


class OrganicChemTestAnswerView(TemplateView):
    """ выводит ответ теста - реакцию  по органической химии """
    
    template_name = 'Chem/organiclawtestanswer.html'

    def get_context_data(self, **kwargs):

        # вывод ответа
        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        qw = OrganicReaction.objects.get(pk=ind)
        context['reagent1'] = OrganicReaction.objects.get(pk=ind).reagent1
        context['reagent2'] = OrganicReaction.objects.get(pk=ind).reagent2
        context['reagent3'] = OrganicReaction.objects.get(pk=ind).reagent3
        context['condition'] = OrganicReaction.objects.get(pk=ind).condition
        context['product1'] = OrganicReaction.objects.get(pk=ind).product1
        context['product2'] = OrganicReaction.objects.get(pk=ind).product2
        context['product3'] = OrganicReaction.objects.get(pk=ind).product3
        context['product4'] = OrganicReaction.objects.get(pk=ind).product4


        
        name1 = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('name', flat=True).first() or ""
        name2 = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('name', flat=True).first() or ""
        name3 = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('name', flat=True).first() or ""
        context['name1'] = name1
        context['name2'] = name2
        context['name3'] = name3

        pkc1 = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('pk', flat=True).first() or ""
        pkc2 = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('pk', flat=True).first() or ""
        pkc3 = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('pk', flat=True).first() or ""

        
        name4 = NamesCompaunds.objects.filter(formula=qw.product1).values_list('name', flat=True).first() or ""
        name5 = NamesCompaunds.objects.filter(formula=qw.product2).values_list('name', flat=True).first() or ""
        name6 = NamesCompaunds.objects.filter(formula=qw.product3).values_list('name', flat=True).first() or ""
        name7 = NamesCompaunds.objects.filter(formula=qw.product4).values_list('name', flat=True).first() or ""
        context['name4'] = name4
        context['name5'] = name5
        context['name6'] = name6
        context['name7'] = name7

        pkc4 = OrganicNames.objects.filter(name1=qw.product1).values_list('pk', flat=True).first() or ""
        pkc5 = OrganicNames.objects.filter(name1=qw.product2).values_list('pk', flat=True).first() or ""
        pkc6 = OrganicNames.objects.filter(name1=qw.product3).values_list('pk', flat=True).first() or ""
        pkc7 = OrganicNames.objects.filter(name1=qw.product4).values_list('pk', flat=True).first() or ""

        my_list = [pkc1, pkc2, pkc3, pkc4, pkc5, pkc6, pkc7]
        new_list = [x if x != "" else 1 for x in my_list]

        context['pkc1'] = new_list[0]
        context['pkc2'] = new_list[1]
        context['pkc3'] = new_list[2]
        context['pkc4'] = new_list[3]
        context['pkc5'] = new_list[4]
        context['pkc6'] = new_list[5]
        context['pkc7'] = new_list[6]


        
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

        correct_count = self.request.session.get('correct_count')
        incorrect_count = self.request.session.get('incorrect_count')
        all_count = self.request.session.get('all_count')
        if all_count == 0:
            percent = 0
        else:
            
            percent = round((correct_count / all_count) * 100)

        
        
        context['next_index'] = next_index
       
        context['items'] = question_list
        context['count'] = len(question_list)
        context['last_list'] = last_list
        context['obj'] = qw
        context['percent'] = percent

        # блок добавки реакций в список любимых авторизованного пользователя
    
        if self.request.user.is_authenticated:
        # Получаем плоский список ID реакций, которые добавил этот пользователь
            context['favorite_ids'] = list(Organic.objects.filter(
                user=self.request.user
            ).values_list('reaction_id', flat=True))
        else:
            context['organic_favorite_ids'] = []
        
        return context

def organic_add_to_list(request, reaction_id):
    if request.method == 'POST':
        reaction = get_object_or_404(OrganicReaction, id=reaction_id)
        # get_or_create гарантирует отсутствие дублей (UniqueTogether)
        OrganicUserReaction.objects.get_or_create(user=request.user, reaction=reaction)
    
    # Возвращаем пользователя обратно
    return redirect(request.META.get('HTTP_REFERER', '/'))


def organic_remove_reaction(request, reaction_id):
    if request.method == 'POST':
        # Находим и удаляем связь текущего пользователя с этой реакцией
        OrganicUserReaction.objects.filter(user=request.user, reaction_id=reaction_id).delete()

    # Возвращаем пользователя туда, откуда он пришел
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def organic_my_reactions_list(request):
    # Получаем все связи текущего пользователя с реакциями
    # select_related('reaction') подгрузит данные InorganicReaction одним запросом
    user_items = OrganicUserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'Chem/organic_my_reactions.html', {'user_items': user_items})



# органические вещества
class OrganicCompaundView(ListView):
    """ Выводит список всех всех веществ """
    model = OrganicNames
    template_name = 'Chem/organiccompaunds.html'
    context_object_name = 'objects'
    ordering = ['pk']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(OrganicCompaundView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class OrganicCompaundStrView(TemplateView):
    """страница химического вещества"""
    template_name = 'Chem/organiccompaund.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        ind=self.kwargs['str']
        objcontent = OrganicNames.objects.get(pk=ind) 
        f = objcontent.name1
        context['objcontent'] = objcontent

        qw = OrganicReaction.objects.filter(Q(reagent1__icontains=f) | Q(reagent2__icontains=f) | Q(reagent3__icontains=f) | Q(product1__icontains=f) | Q(product2__icontains=f) | Q(product3__icontains=f) | Q(product4__icontains=f) )

        context['qw'] = qw
        
        return context

class OrganicCompaundSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по веществам """

    template_name = 'Chem/organiccompaunds.html'

    def get_context_data(self, **kwargs):
        context = super(OrganicCompaundSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = OrganicNames.objects.\
            filter(Q(name1__icontains=searchword)|Q(name1__icontains=searchword1)|Q(name2__icontains=searchword)|Q(name2__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context
