import random
from django.contrib import messages
from django.views.generic import ListView, TemplateView, View, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import *
from rdkit import Chem as Chemredactor

class OrganicChemTestAnswerView(TemplateView):
    """ выводит ответ теста - реакцию по органической химии """
    template_name = 'Chem/organiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs.get('str')
        
        try:
            qw = OrganicReaction.objects.get(pk=ind)
        except OrganicReaction.DoesNotExist:
            from django.http import Http404
            raise Http404("Реакция не найдена")
            
        context['obj'] = qw

        # Список текстовых структур из реакции
        structures = [
            qw.reagent1, qw.reagent2, qw.reagent3, 
            qw.product1, qw.product2, qw.product3, qw.product4
        ]
        
        # Поиск name1 по полю molecule_short
        for i, struct in enumerate(structures, 1):
            if struct:
                # Ищем запись, где molecule_short соответствует тексту из реакции
                name_obj = OrganicNames.objects.filter(molecule_short=struct).first()
                context[f'html_name{i}'] = name_obj.name1 if name_obj else ""
            else:
                context[f'html_name{i}'] = ""

        # Проброс самих формул (для удобства шаблона)
        context['reagent1'] = qw.reagent1
        context['reagent2'] = qw.reagent2
        context['reagent3'] = qw.reagent3
        context['product1'] = qw.product1
        context['product2'] = qw.product2
        context['product3'] = qw.product3
        context['product4'] = qw.product4
        context['condition'] = qw.condition

        # Расчет процентов
        correct_count = self.request.session.get('correct_count', 0) or 0
        all_count = self.request.session.get('all_count', 0) or 0
        context['percent'] = round((correct_count / all_count) * 100) if all_count > 0 else 0

        # Очередь
        last_list = self.request.session.get('organic_question_list', [])
        question_list = list(last_list)
        try:
            next_index = question_list.pop(0)
        except:
            next_index = None
        self.request.session['organic_question_list'] = question_list
        
        context.update({
            'next_index': next_index,
            'count': len(question_list),
            'last_list': last_list,
        })

        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(OrganicUserReaction.objects.filter(
                user=self.request.user
            ).values_list('reaction_id', flat=True))
        else:
            context['favorite_ids'] = []
            
        return context

class OrganicChemTestQuestionView(TemplateView):
    """ Выводит вопрос теста - реакцию по органической химии со структурами """
    template_name = 'Chem/organiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        
        # Получаем объект реакции
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
        # Список реагентов из объекта реакции
        reagents = [qw.reagent1, qw.reagent2, qw.reagent3]
        molecules = []

        for r in reagents:
            if r:
                # Ищем молекулу (SMILES), если реагент совпадает с любым из 4 имен
                mol = OrganicNames.objects.filter(
                    Q(name1=r) | Q(name2=r) | Q(name3=r) | Q(name4=r)
                ).values_list('molecule', flat=True).first()
                molecules.append(mol or "")
            else:
                molecules.append("")

        # Раскладываем структуры (SMILES) по контексту
        context.update({
            'molecule1': molecules[0],
            'molecule2': molecules[1],
            'molecule3': molecules[2],
            'reagent1': qw.reagent1,
            'reagent2': qw.reagent2,
            'reagent3': qw.reagent3,
            'condition': qw.condition,
            'form': Unswer4Form(), # Предполагаем, что форма та же
            'q1': ind,
            'obj': qw,
            'items': self.request.session.get('question_list', []),
            'count': len(self.request.session.get('question_list', [])),
        })

        # Увеличиваем счетчик
        self.request.session['all_count'] = self.request.session.get('all_count', 0) + 1
        
        return context

    def post(self, request, *args, **kwargs):
        ind = int(self.kwargs['str'])
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
        # Синонимы для отсутствия ответа
        no_ans = ["not", "ytn", "нет", "none", "-"]
        
        raw_fields = ['field1', 'field2', 'field3', 'field4']
        user_answers = []

        for f in raw_fields:
            val = request.POST.get(f, '').strip()
            if val:
                if val.lower() in no_ans:
                    user_answers.append("нет")
                else:
                    user_answers.append(val)

        # Продукты из базы
        correct_answers = list(filter(None, [qw.product1, qw.product2, qw.product3, qw.product4]))
        
        # Сравнение без учета регистра и порядка
        user_upper = sorted([a.upper() for a in user_answers])
        correct_upper = sorted([c.upper() for c in correct_answers])

        answer_display = " + ".join(user_answers)

        if user_upper == correct_upper:
            messages.success(request, "Верно!")
            self.request.session['correct_count'] = self.request.session.get('correct_count', 0) + 1
        else:
            messages.error(request, f'Не верно :( . Ваш ответ: {answer_display}')
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1
            
        request.session['answer_list'] = [request.POST.get(f, '') for f in raw_fields]
        return redirect('organiclawtestanswer', str=ind)





# тесты на названия органики
# 1. ВЫБОР РЕЖИМА (Пульт управления)
class OrganicNamesTestHeadView(View):
    def get(self, request):
        return render(request, 'Chem/organicnames_test_head.html')

# 2. ПОДГОТОВКА (Превью и инициализация сессии)
class OrganicNamesTestStartView(View):
    def get(self, request):
        # Принудительно берем режим из URL
        mode = request.GET.get('mode', 'name_to_mol')
        # Сохраняем его временно, чтобы показать в шаблоне
        return render(request, 'Chem/organicnamestest_start.html', {'mode': mode})

    def post(self, request):
        # 1. Получаем режим из скрытого поля формы или из URL
        mode = request.POST.get('mode') or request.GET.get('mode') or 'name_to_mol'
        
        # 2. ПОЛНОЕ УДАЛЕНИЕ СТАРОЙ СЕССИИ (Чистим 8/4 и прочее)
        request.session.flush() 
        
        # 3. Начинаем выборку заново
        queryset = OrganicNames.objects.all()
        if mode == 'form_to_class':
            queryset = queryset.exclude(formula__isnull=True).exclude(formula__exact='')
        
        ids = list(queryset.values_list('id', flat=True))
        random.shuffle(ids)
        
        # 4. ЗАПИСЫВАЕМ ЧИСТЫЕ ДАННЫЕ
        request.session['organicnamestest_ids'] = ids[:10] # Строго 10 вопросов
        request.session['organicnamestest_score'] = 0      # Строго НОЛЬ баллов
        request.session['organicnamestest_mode'] = mode
        
        # 5. Принудительно сохраняем
        request.session.modified = True
        
        return redirect('organicnamestest_question', index=0)

# 3. СТРАНИЦА ВОПРОСА
class OrganicNamesTestQuestionView(View):
    def get(self, request, index):
        test_ids = request.session.get('organicnamestest_ids', [])
        mode = request.session.get('organicnamestest_mode', 'name_to_mol')

        if not test_ids or index >= len(test_ids):
            return redirect('organicnamestest_finished')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        
        context = {
            'molecule': obj,
            'index': index,
            'mode': mode,
            'total_questions': len(test_ids),
            'organic_classes': ORGANIC_CLASSES
        }
        
        template_name = f'Chem/organicnamestest_question_{mode}.html'
        return render(request, template_name, context)

# 4. ПРОВЕРКА ОТВЕТА
class OrganicNamesTestAnswerView(View):
    def post(self, request, index):
        mode = request.session.get('organicnamestest_mode', 'name_to_mol')
        # Собираем ответ из разных типов полей
        user_ans = request.POST.get('user_answer') or request.POST.get('user_smiles') or ""
        user_ans = user_ans.strip()
        
        test_ids = request.session.get('organicnamestest_ids', [])
        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        
        is_correct = False
        user_label = user_ans

        # Логика сравнения
        if mode == 'name_to_mol':
            m1 = Chemredactor.MolFromSmiles(user_ans)
            m2 = Chemredactor.MolFromSmiles(obj.molecule)
            if m1 and m2:
                is_correct = Chemredactor.MolToSmiles(m1) == Chemredactor.MolToSmiles(m2)
        
        elif mode == 'mol_to_name':
            is_correct = user_ans.lower() == obj.name1.lower()
            
        elif mode == 'form_to_class':
            is_correct = (user_ans == obj.organic_class)
            # Заменяем код (alkanes) на название (Алканы) для отображения
            user_label = dict(ORGANIC_CLASSES).get(user_ans, "Не выбрано")

        # Начисляем баллы
        if is_correct:
            request.session['organicnamestest_score'] = request.session.get('organicnamestest_score', 0) + 1
            request.session.modified = True

        return render(request, 'Chem/organicnamestest_answer.html', {
            'molecule': obj,
            'is_correct': is_correct,
            'user_answer_label': user_label,
            'next_index': index + 1,
            'total_questions': len(test_ids),
            'mode': mode
        })

# 5. ФИНАЛ
class OrganicNamesTestFinishedView(View):
    def get(self, request):
        score = request.session.get('organicnamestest_score', 0)
        test_ids = request.session.get('organicnamestest_ids', [])
        total = len(test_ids)
        
        if total == 0:
            return redirect('organicnamestest_head')

        percent = int((score / total) * 100)
        
        return render(request, 'Chem/organicnamestest_finished.html', {
            'score': score,
            'total': total,
            'percent': percent
        })



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


class OrganicLawTestHeadView(TemplateView):
    template_name = 'Chem/organiclawtesthead.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Берем num из URL (теперь ключи совпадают)
        num = self.kwargs['num'] 
        
        # Получаем объект темы для заголовков
        # (Замените OrganicLaw на ваше название модели тем)
        topic = get_object_or_404(Organiclaw, pk=num) 
        
        # 1. Формируем список ID реакций, привязанных к этой теме
        # Убедитесь, что поле связи в OrganicReaction называется 'number'
        question_list = list(OrganicReaction.objects.filter(number=topic).values_list('pk', flat=True))
        
        import random
        random.shuffle(question_list)

        # 2. Инициализируем сессию для органики
        self.request.session['question_list'] = question_list
        self.request.session['all_count'] = 0
        self.request.session['correct_count'] = 0
        self.request.session['incorrect_count'] = 0

        # 3. Передаем данные в шаблон
        if question_list:
            # Извлекаем первый ID для кнопки "Перейти к вопросам"
            # Важно: используем копию, чтобы не испортить список в сессии раньше времени
            context['q1'] = question_list[0]
        else:
            context['q1'] = None

        context['count'] = len(question_list)
        context['numbertitle'] = topic.metatitle # Название темы
        context['obj'] = topic
        
        return context


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
            context['favorite_ids'] = list(OrganicUserReaction.objects.filter(
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
