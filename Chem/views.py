import random
from django.contrib import messages
from django.views.generic import ListView, TemplateView, View, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import *
from rdkit import Chem as Chemredactor
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import Http404

class OrganicLawTestHeadView(TemplateView):
    template_name = 'Chem/organiclawtesthead.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num = self.kwargs['num']
        
        topic = get_object_or_404(Organiclaw, pk=num)
        reactions = OrganicReaction.objects.filter(number=topic)
        
        # Уникальный ключ для органики (например, "org_12")
        current_test_id = f"org_{num}"
        session = self.request.session

        # ПРОВЕРКА: Если в сессии пусто или зашли в другой раздел — создаем список
        if 'question_list' not in session or session.get('active_test') != current_test_id:
            question_ids = list(reactions.values_list('pk', flat=True))
            random.shuffle(question_ids)
            
            session['question_list'] = question_ids
            session['active_test'] = current_test_id
            session['all_count'] = 0
            session['correct_count'] = 0
            session['incorrect_count'] = 0
            session.modified = True

        current_list = session.get('question_list', [])

        context['numbertitle'] = topic.title
        context['count'] = reactions.count()
        context['obj'] = topic
        context['q1'] = current_list[0] if current_list else 0
        
        return context

class OrganicChemTestQuestionView(TemplateView):
    """ Выводит вопрос теста — только текст реакции и условия """
    template_name = 'Chem/organiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
        context.update({
            'reagent1': qw.reagent1,
            'reagent2': qw.reagent2,
            'reagent3': qw.reagent3,
            'condition': qw.condition,
            'form': OrganicTestForm(),
            'q1': ind,
            'obj': qw,
            'items': self.request.session.get('question_list', []),
        })
        # УБРАЛИ ОТСЮДА self.request.session['all_count'] += 1
        return context

    def post(self, request, *args, **kwargs):
        ind = int(self.kwargs['str'])
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
        no_ans = ["not", "ytn", "нет", "none", "-"]
        user_answers = []
        for f in ['field1', 'field2', 'field3', 'field4']:
            val = request.POST.get(f, '').strip()
            if val:
                user_answers.append("нет" if val.lower() in no_ans else val)

        correct_list = [str(c).strip() for c in [qw.product1, qw.product2, qw.product3, qw.product4] if c]
        user_upper = sorted([a.upper() for a in user_answers])
        correct_upper = sorted([c.upper() for c in correct_list])

        if not user_answers:
            messages.warning(request, "Нет ответа")
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1
        elif user_upper == correct_upper:
            messages.success(request, "Верно!")
            self.request.session['correct_count'] = self.request.session.get('correct_count', 0) + 1
        else:
            messages.error(request, 'Не верно :(')
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1
            
        # СЧЕТЧИК ОБНОВЛЯЕТСЯ ТОЛЬКО ПРИ POST ЗАПРОСЕ
        self.request.session['all_count'] = self.request.session.get('all_count', 0) + 1
        self.request.session.modified = True 

        return redirect('organiclawtestanswer', str=ind)


class OrganicChemTestAnswerView(TemplateView):
    template_name = 'Chem/organiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs.get('str')
        qw = get_object_or_404(OrganicReaction, pk=ind)
        context['obj'] = qw

        # ПОИСК СОЕДИНЕНИЙ (без изменений)
        struct_list = [qw.reagent1, qw.reagent2, qw.reagent3, qw.product1, qw.product2, qw.product3, qw.product4]
        for i, val in enumerate(struct_list, 1):
            target = str(val).strip() if val else None
            found_obj = OrganicNames.objects.filter(molecule_short__iexact=target).first() if target else None
            context[f'obj_n{i}'] = found_obj

        # ИЗБРАННОЕ
        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(OrganicUserReaction.objects.filter(user=self.request.user).values_list('reaction_id', flat=True))
        else:
            context['favorite_ids'] = []

        # СТАТИСТИКА
        all_c = self.request.session.get('all_count', 0)
        corr_c = self.request.session.get('correct_count', 0)
        context['percent'] = round((corr_c / all_c) * 100) if all_c > 0 else 0
        
        # ОЧЕРЕДЬ ТЕСТА (БЕЗ УДАЛЕНИЯ ПО F5)
        q_list = self.request.session.get('question_list', [])
        next_id = None
        
        if q_list:
            try:
                # Ищем текущий ID в списке и берем следующий за ним
                current_pos = q_list.index(int(ind))
                if current_pos + 1 < len(q_list):
                    next_id = q_list[current_pos + 1]
            except (ValueError, TypeError):
                # Если текущий ID не найден, берем первый из списка
                next_id = q_list[0] if q_list else None
            
        context['next_index'] = next_id
        context['count'] = len(q_list)
        return context











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
    """ выводит заглавную страницу теста по неорганической химии """
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super(ChemTestHeadView, self).get_context_data(**kwargs)
        str_pk = self.kwargs['str']
        
        try:
            reactions = InorganicReaction.objects.filter(number__pk=str_pk)
            a = reactions.first()
            context['numbertitle'] = a.number.title if a else 'Пока нет реакций'
            context['count'] = reactions.count()

            # ПРОВЕРКА: Создаем список в сессии ТОЛЬКО если его там еще нет
            # или если пользователь зашел в другой раздел теста (с другим str_pk)
            # (необязательно, но полезно добавить проверку на смену раздела теста)
            if 'question_list' not in self.request.session or not self.request.session['question_list']:
                question_ids = list(reactions.values_list('id', flat=True))
                random.shuffle(question_ids)
                
                # Инициализируем сессию только один раз при старте
                self.request.session['question_list'] = question_ids
                self.request.session['correct_count'] = 0
                self.request.session['incorrect_count'] = 0
                self.request.session['all_count'] = 0
            
            # Извлекаем текущий список из сессии
            current_list = self.request.session.get('question_list', [])

            if current_list:
                # ВАЖНО: Мы НЕ используем .pop(0) здесь.
                # Просто берем ID первого вопроса для кнопки "Начать/Продолжить"
                context['q1'] = current_list[0]
                context['question_ids'] = current_list[1:] # Остальные для инфо
            else:
                context['q1'] = 0
                context['question_ids'] = []

        except Exception as e:
            context['numbertitle'] = 'Ошибка загрузки'
            context['count'] = ''
            context['question_ids'] = '' 
            context['q1'] = 0
            
        return context

    def get_queryset(self):
        str_pk = self.kwargs['str']
        return InorganicReaction.objects.filter(number__pk=str_pk)


class ChemMyTestHeadView(ListView):
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_queryset(self):
        return InorganicReaction.objects.filter(
            userreaction__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        if queryset.exists():
            context['numbertitle'] = "Мои сохраненные реакции"
            context['count'] = queryset.count()
            
            # --- ЛОГИКА СОХРАНЕНИЯ СПИСКА ---
            # Проверяем, есть ли уже активный тест в сессии. 
            # Если списка нет или он пуст — генерируем новый.
            if 'question_list' not in self.request.session or not self.request.session['question_list']:
                question_ids = list(queryset.values_list('id', flat=True))
                random.shuffle(question_ids)
                
                # Записываем в сессию НОВЫЙ список и обнуляем счетчики
                self.request.session['question_list'] = question_ids
                self.request.session['correct_count'] = 0
                self.request.session['incorrect_count'] = 0
                self.request.session['all_count'] = 0
            
            # Получаем актуальный список из сессии
            current_ids = self.request.session.get('question_list', [])
            
            if current_ids:
                # ВАЖНО: Мы НЕ делаем .pop(0) здесь. 
                # Мы просто берем первый элемент для отображения.
                # Удалим его только тогда, когда юзер РЕАЛЬНО ответит (в POST-запросе).
                context['q1'] = current_ids[0]
                context['question_ids'] = current_ids[1:] # остаток для отображения (если нужно)
            else:
                context['q1'] = 0
        else:
            context['numbertitle'] = 'В вашем списке пока нет реакций'
            context['count'] = 0
            context['q1'] = 0
            
        return context




class ChemTestQuestionView(TemplateView):
    """ Выводит вопрос теста по неорганической химии """
    template_name = 'Chem/inorganiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']

        # Просто читаем список из сессии, ничего не удаляя (без pop)
        my_data = self.request.session.get('question_list', [])
        qw = get_object_or_404(InorganicReaction, pk=ind)
        
        # Получаем русские названия веществ (если есть)
        def get_name(formula):
            if not formula: return ""
            return NamesCompaunds.objects.filter(formula=formula).values_list('name', flat=True).first() or ""

        context.update({
            'name1': get_name(qw.reagent1),
            'name2': get_name(qw.reagent2),
            'name3': get_name(qw.reagent3),
            'reagent1': qw.reagent1,
            'reagent2': qw.reagent2,
            'reagent3': qw.reagent3,
            'condition': qw.condition,
            'form': Unswer4Form(),
            'q1': ind,
            'obj': qw,
            'items': my_data,
            'count': len(my_data)
        })
        
        # ВАЖНО: Мы убрали отсюда self.request.session['all_count'] += 1
        # Теперь обновление страницы (F5) не накручивает счетчик вопросов.
        
        return context

    def post(self, request, *args, **kwargs):
        ind = int(self.kwargs['str'])
        qw = get_object_or_404(InorganicReaction, pk=ind)
        
        # Сбор данных из формы
        p1 = request.POST.get('field1', '').strip()
        p2 = request.POST.get('field2', '').strip()
        p3 = request.POST.get('field3', '').strip()
        p4 = request.POST.get('field4', '').strip()
        
        answer_list = [p1, p2, p3, p4]
        correct_answers = [qw.product1, qw.product2, qw.product3, qw.product4]

        # Функция для нормализации (удаление пустых, регистр, обработка "нет")
        def normalize(val):
            if not val: return None
            v = val.lower()
            return "НЕТ" if v in ["not", "ytn", "нет", "no"] else val.upper()

        clean_user = [normalize(x) for x in answer_list if x]
        clean_corr = [normalize(x) for x in correct_answers if x]

        # 1. Логика проверки ответа
        if not clean_user:
            # Если пользователь ничего не ввел
            messages.warning(request, "Нет ответа")
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1
        
        elif sorted(clean_user) == sorted(clean_corr):
            # Если ответ верный
            messages.success(request, "Верно!")
            self.request.session['correct_count'] = self.request.session.get('correct_count', 0) + 1
            
        else:
            # Если ответ неверный
            user_ans_str = " + ".join(filter(None, answer_list))
            messages.error(request, f'Не верно :( .Ваш ответ: {user_ans_str}')
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1

        # 2. Обновляем счетчик попыток именно здесь (после нажатия кнопки)
        self.request.session['all_count'] = self.request.session.get('all_count', 0) + 1
        self.request.session['answer_list'] = answer_list
        
        # Сообщаем Django, что сессия изменена
        self.request.session.modified = True

        return redirect('inorganiclawtestanswer', str=ind)
        


class ChemTestAnswerView(TemplateView):
    template_name = 'Chem/inorganiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        
        # Получаем текущую реакцию
        qw = get_object_or_404(InorganicReaction, pk=ind)
        context['obj'] = qw # Важно для шаблона!

        # 1. Вспомогательная функция для названий соединений
        def get_comp_info(formula):
            if not formula: 
                return {"name": "", "pk": 1}
            obj = NamesCompaunds.objects.filter(formula=formula).first()
            return {
                "name": obj.name if obj else formula, # если нет в базе, вернет формулу
                "pk": obj.pk if obj else 1
            }

        # Наполняем контекст реагентами и продуктами
        reagents = [qw.reagent1, qw.reagent2, qw.reagent3]
        products = [qw.product1, qw.product2, qw.product3, qw.product4]
        
        for i, f in enumerate(reagents, 1):
            info = get_comp_info(f)
            context[f'reagent{i}'] = f
            context[f'name{i}'] = info['name']
            context[f'pkc{i}'] = info['pk']

        for i, f in enumerate(products, 1):
            info = get_comp_info(f)
            context[f'product{i}'] = f
            context[f'name{i+3}'] = info['name']
            context[f'pkc{i+3}'] = info['pk']

        context['condition'] = qw.condition

        # 2. Логика навигации (следующий вопрос)
        question_list = self.request.session.get('question_list', [])
        next_index = None
        
        if question_list:
            try:
                # Преобразуем ind в int, так как в сессии хранятся числа
                current_id = int(ind)
                if current_id in question_list:
                    current_pos = question_list.index(current_id)
                    if current_pos + 1 < len(question_list):
                        next_index = question_list[current_pos + 1]
            except (ValueError, TypeError):
                pass

        # 3. Статистика
        correct_count = self.request.session.get('correct_count', 0)
        all_count = self.request.session.get('all_count', 0)
        percent = round((correct_count / all_count) * 100) if all_count > 0 else 0

        context.update({
            'next_index': next_index,
            'percent': percent,
            'count': len(question_list)
        })

        # 4. ИЗБРАННОЕ (Чтобы кнопки "Удалить/Добавить" работали)
        if self.request.user.is_authenticated:
            # Получаем список ID всех реакций, которые этот юзер сохранил
            # ВАЖНО: убедитесь, что поле в UserReaction называется 'reaction'
            fav_ids = UserReaction.objects.filter(
                user=self.request.user
            ).values_list('reaction_id', flat=True)
            
            context['favorite_ids'] = list(fav_ids) # Превращаем QuerySet в список
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





class OrganicChemMyTestHeadView(ListView):
    template_name = 'Chem/organiclawtesthead.html'
    context_object_name = 'objects'

    def get_queryset(self):
        return OrganicReaction.objects.filter(
            organic_userreaction__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        if queryset.exists():
            context['numbertitle'] = "Мои сохраненные реакции"
            context['count'] = queryset.count()
            
            # ПРОВЕРКА: Инициализируем тест только если списка еще нет в сессии
            if 'question_list' not in self.request.session or not self.request.session['question_list']:
                question_ids = list(queryset.values_list('id', flat=True))
                random.shuffle(question_ids)
                
                # Сохраняем начальное состояние
                self.request.session['question_list'] = question_ids
                self.request.session['correct_count'] = 0
                self.request.session['incorrect_count'] = 0
                self.request.session['all_count'] = 0
            
            # Получаем актуальный список из сессии БЕЗ pop(0)
            current_ids = self.request.session.get('question_list', [])
            
            if current_ids:
                # Первый ID для старта/продолжения теста
                context['q1'] = current_ids[0]
                # Остаток списка для передачи в шаблон (если нужно)
                context['question_ids'] = current_ids[1:]
            else:
                context['q1'] = 0
        else:
            context['numbertitle'] = 'В вашем списке пока нет реакций'
            context['count'] = 0
            context['q1'] = 0
            
        return context





    


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



def organic_add_to_list(request, reaction_id):
    """ Добавление органической реакции в список пользователя """
    if request.user.is_authenticated:
        # Используем get_or_create, чтобы не плодить дубликаты
        OrganicUserReaction.objects.get_or_create(
            user=request.user, 
            reaction_id=reaction_id
        )
    return redirect(request.META.get('HTTP_REFERER', '/'))

def organic_remove_reaction(request, reaction_id):
    """ Удаление органической реакции из списка пользователя """
    if request.user.is_authenticated:
        OrganicUserReaction.objects.filter(
            user=request.user, 
            reaction_id=reaction_id
        ).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def organic_my_reactions_list(request):
    """Выводит список всех избранных органических реакций пользователя"""
    # Получаем все объекты связей пользователя с реакциями
    my_reactions = OrganicUserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'Chem/organic_my_list.html', {
        'my_reactions': my_reactions
    })



class OrganicFavoritesTestHeadView(LoginRequiredMixin, View):
    """Голова теста для избранных реакций по органике"""
    
    def get(self, request):
        # Получаем список ID реакций через related_name
        fav_ids = list(request.user.organic_favorite_reactions.values_list('reaction_id', flat=True))
        
        if not fav_ids:
            # Если список пуст, можно выкинуть сообщение или просто вернуть в профиль
            return redirect('profile')

        # Перемешиваем список для эффекта теста
        random.shuffle(fav_ids)

        # Инициализируем стандартную сессию для органического теста
        request.session['question_list'] = fav_ids
        request.session['all_count'] = 0
        request.session['correct_count'] = 0
        request.session['incorrect_count'] = 0
        
        # Берем первый ID из списка
        first_question_id = fav_ids[0]
        
        # Перенаправляем на стандартную вьюшку вопроса (которую мы правили ранее)
        return redirect('organiclawtestquestion', str=first_question_id)
