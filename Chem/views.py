import random
from django.views import View
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
from django.db.models import F




from .models import OrganicNames, UserQuestionProgress  # Подключаем модель прогресса

# =====================================================================
# 🧬 БЛОК VIEWS ДЛЯ СИСТЕМЫ ТЕСТИРОВАНИЯ ПОЛИМЕРОВ
# =====================================================================

# =====================================================================
# 0. ГЛАВНАЯ СТРАНИЦА ВЫБОРА РЕЖИМА ПОЛИМЕРОВ (ПУЛЬТ УПРАВЛЕНИЯ)
# =====================================================================
class PolymerTestHeadView(View):
    def get(self, request):
        return render(request, 'Chem/polymertest_head.html')


# =====================================================================
# 1. ПУЛЬТ УПРАВЛЕНИЯ И СТАРТ ТЕСТА ПОЛИМЕРОВ (ФИЛЬТРАЦИЯ ПО ТИПАМ)
# =====================================================================
class PolymerTestStartView(View):
    def get(self, request):
        # Получаем выбранный режим теста из GET-параметров
        mode = request.GET.get('mode', 'monomer_to_polymer')
        # Восстанавливаем из сессии типы полимеров, выбранные пользователем ранее
        previously_selected_types = request.session.get('polymer_last_selected_types', [])
        
        # Формируем список чекбоксов на основе вашего POLYMER_TYPE_CHOICES
        selectable_groups = []
        for type_slug, type_name in POLYMER_TYPE_CHOICES:
            selectable_groups.append({
                'slug': type_slug,
                'name': type_name,
                'is_checked': type_slug in previously_selected_types or not previously_selected_types
            })

        context = {
            'mode': mode,
            'selectable_groups': selectable_groups,
        }
        return render(request, 'Chem/polymertest_start.html', context)

    def post(self, request):
        # Определяем рабочий режим тестирования
        mode = request.POST.get('mode') or request.GET.get('mode') or 'monomer_to_polymer'
        # Считываем отмеченные пользователем типы полимеров (slug-коды)
        selected_types = request.POST.getlist('selected_groups')

        # Сохраняем текущий выбор типов в сессию пользователя
        request.session['polymer_last_selected_types'] = selected_types

        # Полностью сбрасываем состояние и счетчики предыдущего теста
        for key in ['polymertest_ids', 'polymertest_score', 'polymertest_mode', 'polymertest_allowed_types']:
            request.session.pop(key, None)

        # Если пользователь не выбрал ни одного чекбокса, то по умолчанию берем вообще все типы
        if not selected_types:
            selected_types = [t[0] for t in POLYMER_TYPE_CHOICES]

        # Запрашиваем из базы только видимые записи, у которых тип совпадает с выбранными
        queryset = OrganicNames.objects.filter(polymer_type__in=selected_types, is_visible=True)
        
        # Фильтруем пустые записи под конкретный режим
        if mode == 'monomer_to_polymer':
            queryset = queryset.exclude(monomer_name__isnull=True).exclude(monomer_name__exact='')
        elif mode == 'polymer_to_type':
            queryset = queryset.exclude(polymer_type__isnull=True).exclude(polymer_type__exact='')
        elif mode == 'appearance_to_polymer':
            queryset = queryset.exclude(appearance__isnull=True).exclude(appearance__exact='')

        # --- СИСТЕМА ИНТЕРВАЛЬНОГО ПОВТОРЕНИЯ ДЛЯ ПОЛИМЕРОВ (КАК В ОРГАНИКЕ) ---
        if request.user.is_authenticated:
            # Уменьшаем счетчик пропуска на 1 для всех отложенных вопросов пользователя
            from django.db.models import F
            UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).update(
                skip_count=F('skip_count') - 1
            )
            # Собираем ID вопросов, которые пользователю пока рано видеть
            skipped_ids = UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).values_list('question_id', flat=True)
            queryset_filtered = queryset.exclude(id__in=skipped_ids)
            
            # Исключаем выученные вопросы только если оставшихся хватит на полноценный тест (минимум 10)
            if queryset_filtered.count() >= 10:
                queryset = queryset_filtered

        # Балансировка вопросов: группируем пулы теперь по polymer_type, чтобы темы чередовались
        raw_questions = queryset.values('id', 'polymer_type')
        type_pools = {}
        for q in raw_questions:
            type_pools.setdefault(q['polymer_type'], []).append(q['id'])
            
        # Случайно перемешиваем вопросы внутри каждого отдельного типа
        for t_slug in type_pools:
            random.shuffle(type_pools[t_slug])

        # Алгоритм циклического отбора до 10 вопросов из разных типов полимеров
        final_ids = []
        target_questions_count = 10
        active_slugs = list(type_pools.keys())
        random.shuffle(active_slugs)

        while len(final_ids) < target_questions_count and active_slugs:
            for t_slug in list(active_slugs):
                if type_pools[t_slug]:
                    q_id = type_pools[t_slug].pop(0)
                    final_ids.append(q_id)
                    if len(final_ids) == target_questions_count:
                        break
                else:
                    active_slugs.remove(t_slug)
                    
        # Итоговое перемешивание результирующего списка
        random.shuffle(final_ids)

        # Сохраняем параметры новой сессии тестирования
        request.session['polymertest_ids'] = final_ids
        request.session['polymertest_score'] = 0
        request.session['polymertest_mode'] = mode
        request.session['polymertest_allowed_types'] = selected_types
        request.session.modified = True
        
        return redirect('polymertest_question', index=0)
# =====================================================================
# 2. СТРАНИЦА ТЕКУЩЕГО ВОПРОСА
# =====================================================================
class PolymerTestQuestionView(View):
    def get(self, request, index):
        # Извлекаем пул сгенерированных ID и выбранный режим теста из сессии
        test_ids = request.session.get('polymertest_ids', [])
        mode = request.session.get('polymertest_mode', 'monomer_to_polymer')

        # Если тест пуст или индекс вышел за границы — отправляем на финал
        if not test_ids or index >= len(test_ids):
            return redirect('polymertest_finished')

        # Загружаем текущий объект полимера
        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        options = []

        # Очистка текста от фразы-подсказки для режима внешнего вида
        if mode == 'appearance_to_polymer' and obj.appearance:
            phrase_to_remove = "приведена структурная формула мономера"
            if phrase_to_remove in obj.appearance.lower():
                start_idx = obj.appearance.lower().find(phrase_to_remove)
                exact_phrase = obj.appearance[start_idx:start_idx + len(phrase_to_remove)]
                obj.appearance = obj.appearance.replace(exact_phrase, "")

        # Генерация вариантов ответов под ваш режим: Полимер -> Тип полимера
        if mode == 'polymer_to_type':
            # Добавляем строку-код текущего типа полимера
            options.append(obj.polymer_type)
            
            # Сравниваем строку-код obj.polymer_type со строкой-кодом t_slug из кортежа (t_slug, t_name)
            all_types = [t_slug for t_slug, t_name in POLYMER_TYPE_CHOICES if t_slug != obj.polymer_type]
            random.shuffle(all_types)
            
            # Добираем остальные коды типов, чтобы вариантов стало ровно 4
            while len(options) < 4 and all_types:
                options.append(all_types.pop(0))
            random.shuffle(options)
            
            # Превращаем коды в пары (код, текстовое_название) для шаблона
            type_dict = dict(POLYMER_TYPE_CHOICES)
            options = [(opt, type_dict.get(opt, opt)) for opt in options]

        # Для остальных режимов (текстовый ввод) варианты не генерируются
        elif mode in ['monomer_to_polymer', 'appearance_to_polymer']:
            pass

        context = {
            'polymer': obj,
            'index': index,
            'mode': mode,
            'total_questions': len(test_ids),
            'test_options': options
        }
        return render(request, f'Chem/polymertest_question_{mode}.html', context)


# =====================================================================
# 3. ОБРАБОТКА И ПРОВЕРКА ОТВЕТА (ТОЧНОЕ СРАВНЕНИЕ С NAME1-NAME4)
# =====================================================================
class PolymerTestAnswerView(View):
    def post(self, request, index):
        mode = request.session.get('polymertest_mode', 'monomer_to_polymer')
        user_ans = (request.POST.get('user_answer') or "").strip()
        
        test_ids = request.session.get('polymertest_ids', [])
        if not test_ids or index >= len(test_ids):
            return redirect('polymertest_start')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        is_correct = False
        user_label = user_ans

        if mode == 'polymer_to_type':
            is_correct = (user_ans == obj.polymer_type)
            type_dict = dict(POLYMER_TYPE_CHOICES)
            user_label = type_dict.get(user_ans, "Не выбрано")
            correct_label = type_dict.get(obj.polymer_type, "")

        elif mode in ['monomer_to_polymer', 'appearance_to_polymer']:
            # Собираем все непустые названия полимера из полей name1, name2, name3, name4
            valid_names = []
            for name in [obj.name1, obj.name2, obj.name3, obj.name4]:
                if name and str(name).strip():
                    valid_names.append(str(name).strip().lower())
            
            # Проверяем, совпадает ли введенный пользователем ответ хотя бы с одним полем
            is_correct = user_ans.lower() in valid_names
            user_label = user_ans if user_ans else "Ничего не введено"
            correct_label = obj.name1

        # --- ФИКСАЦИЯ ПРОГРЕССА ДЛЯ ПОЛИМЕРОВ (КАК В ОРГАНИКЕ) ---
        if request.user.is_authenticated:
            progress, created = UserQuestionProgress.objects.get_or_create(
                user=request.user, question=obj
            )
            # Если ответ правильный — скрываем вопрос на 30 циклов, если ошибка — сбрасываем в 0
            progress.skip_count = 30 if is_correct else 0
            progress.save()

        if is_correct:
            request.session['polymertest_score'] = request.session.get('polymertest_score', 0) + 1
            request.session.modified = True

        return render(request, 'Chem/polymertest_answer.html', {
            'polymer': obj,
            'is_correct': is_correct,
            'user_answer_label': user_label,
            'correct_label': correct_label,
            'next_index': index + 1,
            'total_questions': len(test_ids),
            'mode': mode
        })


# =====================================================================
# 4. СТРАНИЦА ИТОГОВ (ФИНАЛ)
# =====================================================================
class PolymerTestFinishedView(View):
    def get(self, request):
        score = request.session.get('polymertest_score', 0)
        test_ids = request.session.get('polymertest_ids', [])
        total = len(test_ids)
        current_mode = request.session.get('polymertest_mode', 'monomer_to_polymer')

        if total == 0:
            return redirect(f"/chem/polymertest/start/?mode={current_mode}")

        percent = int((score / total) * 100)

        return render(request, 'Chem/polymertest_finished.html', {
            'score': score,
            'total': total,
            'percent': percent,
            'mode': current_mode
        })










# ==============================================================================
# 2. СЛОВАРЬ МЕЖКЛАССОВЫХ ИЗОМЕРОВ (Для создания "умных" вариантов ответов)
# ==============================================================================
CLASS_ISOMERS = {
    'alkenes': 'cycloalkanes',
    'cycloalkanes': 'alkenes',
    'alkynes': 'alkadienes',
    'alkadienes': 'alkynes',
    'alcohols': 'ethers',
    'ethers': 'alcohols',
    'aldehydes': 'ketones',
    'ketones': 'aldehydes',
    'saturated_monobasic_carboxylic_acids': 'esters',
    'esters': 'saturated_monobasic_carboxylic_acids',
    'amino_acids': 'nitro_compounds',
    'nitro_compounds': 'amino_acids',
    # Добавлено для школьной химии / ЕГЭ:
    'primary_amines': 'secondary_amines',
    'secondary_amines': 'primary_amines',
    'tertiary_amines': 'primary_amines',
    'primary_amines': 'tertiary_amines',
    'tertiary_amines': 'secondary_amines',
    'secondary_amines': 'tertiary_amines',
    'Нитрилы': 'Циангидрины',
    'Циангидрины': 'Нитрилы',
}

# ==============================================================================
# 3. СЛОВАРЬ ОБЩИХ ФОРМУЛ (С тегами нижних индексов для вывода в HTML)
# ==============================================================================
CLASS_GENERAL_FORMULAS = {
    'alkanes': 'C<sub>n</sub>H<sub>2n+2</sub>',
    'alkenes': 'C<sub>n</sub>H<sub>2n</sub>',
    'alkynes': 'C<sub>n</sub>H<sub>2n-2</sub>',
    'alkadienes': 'C<sub>n</sub>H<sub>2n-2</sub>',
    'cycloalkanes': 'C<sub>n</sub>H<sub>2n</sub>',
    'arenes': 'C<sub>n</sub>H<sub>2n-6</sub>',
    'alcohols': 'C<sub>n</sub>H<sub>2n+1</sub>OH',
    'diols': 'C<sub>n</sub>H<sub>2n</sub>(OH)<sub>2</sub>',
    'triols': 'C<sub>n</sub>H<sub>2n-1</sub>(OH)<sub>3</sub>',
    'polyols': 'C<sub>n</sub>H<sub>2n+2</sub>O<sub>x</sub>',  # Добавлено
    'phenols': 'C<sub>n</sub>H<sub>2n-7</sub>OH',
    'ethers': 'C<sub>n</sub>H<sub>2n+2</sub>O',
    'aldehydes': 'C<sub>n</sub>H<sub>2n</sub>O',
    'ketones': 'C<sub>n</sub>H<sub>2n</sub>O',
    'saturated_monobasic_carboxylic_acids': 'C<sub>n</sub>H<sub>2n</sub>O<sub>2</sub>',
    'esters': 'C<sub>n</sub>H<sub>2n</sub>O<sub>2</sub>',
    'primary_amines': 'C<sub>n</sub>H<sub>2n+3</sub>N',    # Переименован ключ
    'secondary_amines': 'C<sub>n</sub>H<sub>2n+3</sub>N',  # Добавлено
    'tertiary_amines': 'C<sub>n</sub>H<sub>2n+3</sub>N',   # Добавлено
    'amino_acids': 'NH<sub>2</sub>-CH(R)-COOH',
    'halogen_derivatives': 'C<sub>n</sub>H<sub>2n+1</sub>X',
    'halogen_arenes': 'C<sub>n</sub>H<sub>2n-7</sub>X',
    'Нитрилы': 'C<sub>n</sub>H<sub>2n-1</sub>N',           # Добавлено
    'Ангидриды': '(RCO)<sub>2</sub>O',
}


ORGANIC_GROUPS = [
    {
        'name': 'Углеводороды и их галогенопроизводные',
        'classes': ['alkanes', 'alkenes', 'alkynes', 'alkadienes', 'cycloalkanes', 'arenes', 'Ацетилениды', 'halogen_derivatives', 'halogen_arenes', 'other_halogen_derivatives']
    },
    {
        'name': 'Предельные одноосновные кислородсодержащие соединения',
        'classes': ['alcohols', 'ethers', 'aldehydes', 'ketones', 'saturated_monobasic_carboxylic_acids', 'esters', 'phenols', 'Галогенпроизводные фенолов']
    },
    {
        'name': 'Карбоновые кислоты и их производные',
        'classes': ['saturated_monobasic_carboxylic_acids', 'other_carboxylic_acids', 'carboxylic_acids_salts', 'Ангидриды', 'Хлорангидриды', 'Соли сульфокислоты']
    },
    {
        'name': 'Аминокислоты и белки',
        'classes': ['amino_acids', 'polyfunctional_amino_acids', 'дипептиды', 'proteins']
    },
    {
        'name': 'Прочие азотсодержащие соединения',
        'classes': ['Ароматические амины', 'primary_amines', 'secondary_amines', 'tertiary_amines', 'nitro_compounds', 'Соли аминов', 'Галогениды аминов', 'Нитропроизводные фенола', 'Нитрозамины', 'Нитрилы']
    },
    {
        'name': 'Углеводы',
        'classes': ['carbohydrates']
    },
    {
        'name': 'Полимеры',
        'classes': ['Полимеры']
    },
    {
        'name': 'Остальные органические классы',
        'classes': ['Циклические простые эфиры', 'Ацетали', 'Карбамиды', 'Амиды', 'Феноляты', 'diols', 'triols', 'polyols', 'polyfunctional_alcohols',  'ketals_and_hemiketals', 
                    'fats', 'nucleic_acids', 'thiols', 'heterocycles', 'organometallic_compounds', 'Бифункциональное соединение', 'Циангидрины', 'Алкоголяты металлов']
    }
]



# === 1. ВЫБОР РЕЖИМА (Пульт управления) ===
class OrganicNamesTestHeadView(View):
    def get(self, request):
        return render(request, 'Chem/organicnames_test_head.html')


class OrganicNamesTestStartView(View):
    def get(self, request):
        mode = request.GET.get('mode', 'name_to_mol')
        
        # ЗАПОМИНАНИЕ ВЫБОРА: Достаем ранее выбранные ГРУППЫ из сессии
        previously_selected_groups = request.session.get('last_selected_groups', [])
        
        # ФЛАГ ОТОБРАЖЕНИЯ: Если это режим "Формула -> Класс", то выбор разделов НЕ НУЖЕН
        show_groups = mode != 'form_to_class'
        
        selectable_groups = []
        
        # Собираем список групп только если флаг show_groups равен True
        if show_groups:
            for group in ORGANIC_GROUPS:
                if group.get('classes'):
                    selectable_groups.append({
                        'name': group['name'],
                        'is_checked': group['name'] in previously_selected_groups
                    })

        context = {
            'mode': mode,
            'selectable_groups': selectable_groups,
            'show_groups': show_groups  # Отдаем флаг в HTML-шаблон
        }
        return render(request, 'Chem/organicnamestest_start.html', context)

    def post(self, request):
        mode = request.POST.get('mode') or request.GET.get('mode') or 'name_to_mol'
        
        # Получаем список названий ВЫБРАННЫХ ГРУПП из формы
        selected_group_names = request.POST.getlist('selected_groups')

        # ЗАПОМИНАЕМ ВЫБОР ГРУПП в сессии (только для режимов, где они есть)
        if mode != 'form_to_class':
            request.session['last_selected_groups'] = selected_group_names

        # Очищаем данные старого теста
        for key in ['organicnamestest_ids', 'organicnamestest_score', 'organicnamestest_mode', 'organicnamestest_allowed_keys']:
            request.session.pop(key, None)

        # Раскрываем выбранные ГРУППЫ в плоский список входящих в них КЛАССОВ (slug)
        selected_classes = []
        for group in ORGANIC_GROUPS:
            if mode == 'form_to_class' or group['name'] in selected_group_names or not selected_group_names:
                selected_classes.extend(group['classes'])

        # Если режим "Формула -> Класс", жестко фильтруем классы только разрешенными 19 школьными классами
        if mode == 'form_to_class':
            allowed_keys = [
                'alkanes', 'alkenes', 'alkynes', 'alkadienes', 'cycloalkanes', 'alcohols', 'ethers', 
                'aldehydes', 'ketones', 'saturated_monobasic_carboxylic_acids', 'esters', 'amino_acids', 
                'diols', 'triols', 'phenols', 'primary_amines', 'secondary_amines', 'tertiary_amines', 
                'Ароматические амины', 'halogen_derivatives'
            ]
            selected_classes = [c for c in selected_classes if c in allowed_keys]

        # Загружаем карточки из Базы Данных по выбранному режиму
        queryset = OrganicNames.objects.all()
        if mode == 'name_to_mol':
            queryset = queryset.filter(test_name_to_structure=True)
        elif mode == 'mol_to_name':
            queryset = queryset.filter(test_structure_to_name=True)
        elif mode == 'form_to_class':
            queryset = queryset.filter(test_formula_to_class=True).exclude(formula__isnull=True).exclude(formula__exact='')

        # --- СИСТЕМА ИНТЕРВАЛЬНОГО ПОВТОРЕНИЯ ---
        if request.user.is_authenticated:
            UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).update(
                skip_count=F('skip_count') - 1
            )
            skipped_ids = UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).values_list('question_id', flat=True)
            queryset_filtered = queryset.exclude(id__in=skipped_ids)
            if queryset_filtered.count() >= 10:
                queryset = queryset_filtered

        # Оптимизированная выборка из БД за 1 запрос вместо цикла
        raw_questions = queryset.filter(organic_class__in=selected_classes).values('id', 'organic_class')
        
        class_pools = {}
        for q in raw_questions:
            class_pools.setdefault(q['organic_class'], []).append(q['id'])
            
        for c_slug in class_pools:
            random.shuffle(class_pools[c_slug])

        # === АЛГОРИТМ ФИКСИРОВАННОЙ ДЛИНЫ ТЕСТА С ПЕРЕМЕШИВАНИЕМ КЛАССОВ ===
        final_ids = []
        target_questions_count = 10
        active_slugs = list(class_pools.keys())

        # Перемешиваем сами классы, чтобы тест никогда не стартовал с Алканов
        random.shuffle(active_slugs)

        while len(final_ids) < target_questions_count and active_slugs:
            for c_slug in list(active_slugs):
                if class_pools[c_slug]:
                    q_id = class_pools[c_slug].pop(0)
                    final_ids.append(q_id)
                    if len(final_ids) == target_questions_count:
                        break
                else:
                    active_slugs.remove(c_slug)
                    
        # Дополнительно перемешиваем финальный пул вопросов, чтобы они шли вразнобой
        random.shuffle(final_ids)

        request.session['organicnamestest_ids'] = final_ids
        request.session['organicnamestest_score'] = 0
        request.session['organicnamestest_mode'] = mode
        request.session['organicnamestest_allowed_keys'] = selected_classes
        request.session.modified = True
        return redirect('organicnamestest_question', index=0)
# === 3. СТРАНИЦА ВОПРОСА ===
class OrganicNamesTestQuestionView(View):
    def get(self, request, index):
        test_ids = request.session.get('organicnamestest_ids', [])
        mode = request.session.get('organicnamestest_mode', 'name_to_mol')
        allowed_keys = request.session.get('organicnamestest_allowed_keys', [])

        if not test_ids or index >= len(test_ids):
            return redirect('organicnamestest_finished')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        current_class = obj.organic_class
        
        # ИСПРАВЛЕНИЕ: Правильно сверяем slug (первый элемент кортежа item[0]) со списком разрешенных ключей
        filtered_organic_classes = [
            item for item in ORGANIC_CLASSES if item[0] in allowed_keys
        ]

        # === АЛГОРИТМ УМНЫХ ВАРИАНТОВ ОТВЕТА ДЛЯ РЕЖИМА "ФОРМУЛА -> КЛАСС" ===
        options = []
        if mode == 'form_to_class':
            # 1. Добавляем истинный класс
            options.append(current_class)
            
            # 2. Добавляем его межклассовый изомер из созданного ранее словаря CLASS_ISOMERS
            if 'CLASS_ISOMERS' in globals():
                isomer_class = CLASS_ISOMERS.get(current_class)
                if isomer_class and isomer_class in allowed_keys:
                    options.append(isomer_class)

            # 3. Добираем случайные непересекающиеся классы, чтобы вариантов стало ровно 4
            remaining_classes = [c for c in allowed_keys if c not in options]
            random.shuffle(remaining_classes)
            while len(options) < 4 and remaining_classes:
                options.append(remaining_classes.pop(0))

            # Перемешиваем варианты, чтобы правильный ответ не всегда стоял на первом месте
            random.shuffle(options)

            # Превращаем slug вариантов в человеческие названия (кортежи) для шаблона
            class_dict = dict(ORGANIC_CLASSES)
            options = [(opt, class_dict.get(opt, opt)) for opt in options]

        context = {
            'molecule': obj,
            'index': index,
            'mode': mode,
            'total_questions': len(test_ids),
            'organic_classes': filtered_organic_classes, # Выпадающий список снова заполнен!
            'test_options': options  # Передаем готовые 4 варианта в HTML
        }
        template_name = f'Chem/organicnamestest_question_{mode}.html'
        return render(request, template_name, context)
# === 4. ПРОВЕРКА ОТВЕТА ===
class OrganicNamesTestAnswerView(View):
    def post(self, request, index):
        mode = request.session.get('organicnamestest_mode', 'name_to_mol')
        user_ans = request.POST.get('user_answer') or request.POST.get('user_smiles') or ""
        user_ans = user_ans.strip()
        
        test_ids = request.session.get('organicnamestest_ids', [])
        if not test_ids or index >= len(test_ids):
            return redirect('organicnamestest_head')

        obj = get_object_or_404(OrganicNames, id=test_ids[index])
        is_correct = False
        user_label = user_ans
        both_answers_text = ""
        general_formula = ""

        if mode == 'name_to_mol':
            m1 = Chemredactor.MolFromSmiles(user_ans) if 'Chemredactor' in globals() else None
            m2 = Chemredactor.MolFromSmiles(obj.molecule) if 'Chemredactor' in globals() else None
            if m1 and m2:
                is_correct = Chemredactor.MolToSmiles(m1) == Chemredactor.MolToSmiles(m2)
                
        elif mode == 'mol_to_name':
            valid_names = [name.strip().lower() for name in [obj.name1, obj.name2, obj.name3, obj.name4] if name]
            is_correct = user_ans.lower() in valid_names
            
        elif mode == 'form_to_class':
            correct_class = obj.organic_class
            isomer_class = CLASS_ISOMERS.get(correct_class) if 'CLASS_ISOMERS' in globals() else None
            classes_dict = dict(ORGANIC_CLASSES)
            
            correct_label = classes_dict.get(correct_class, "Неизвестный класс")
            isomer_label = classes_dict.get(isomer_class, "")

            if 'CLASS_GENERAL_FORMULAS' in globals():
                general_formula = CLASS_GENERAL_FORMULAS.get(correct_class, "")

            if user_ans == correct_class or (isomer_class and user_ans == isomer_class):
                is_correct = True

            user_label = classes_dict.get(user_ans, "Не выбрано")
            if isomer_label:
                both_answers_text = f"У данных классов одинаковая брутто-формула. Верны оба ответа: {correct_label} и {isomer_label}."

        # --- ФИКСАЦИЯ ПРОГРЕССА ИНТЕРВАЛЬНОГО ПОВТОРЕНИЯ ---
        if request.user.is_authenticated:
            progress, created = UserQuestionProgress.objects.get_or_create(
                user=request.user, question=obj
            )
            progress.skip_count = 30 if is_correct else 0
            progress.save()

        names_list = []
        for name in [obj.name1, obj.name2, obj.name3, obj.name4]:
            if name is not None and str(name).strip() != "":
                names_list.append(str(name).strip())
        obj.all_names_string = ", ".join(names_list) if names_list else "Название отсутствует"

        if is_correct:
            request.session['organicnamestest_score'] = request.session.get('organicnamestest_score', 0) + 1
            request.session.modified = True

        return render(request, 'Chem/organicnamestest_answer.html', {
            'molecule': obj,
            'is_correct': is_correct,
            'user_answer_label': user_label,
            'both_answers_text': both_answers_text,
            'general_formula': general_formula,
            'next_index': index + 1,
            'total_questions': len(test_ids),
            'mode': mode
        })


# === 5. ФИНАЛ ===
class OrganicNamesTestFinishedView(View):
    def get(self, request):
        score = request.session.get('organicnamestest_score', 0)
        test_ids = request.session.get('organicnamestest_ids', [])
        total = len(test_ids)

        # Вытаскиваем режим перед возможной очисткой
        current_mode = request.session.get('organicnamestest_mode', 'name_to_mol')

        if total == 0:
            # ИСПРАВЛЕНИЕ: Перенаправляем на страницу настройки конкретного режима
            return redirect(f"/chem/organicnamestest/start/?mode={current_mode}")

        percent = int((score / total) * 100)
        
        # === СТАЛО: Сохраняем режим и передаем его в контекст ===
        current_mode = request.session.get('organicnamestest_mode', 'name_to_mol')

        return render(request, 'Chem/organicnamestest_finished.html', {
            'score': score,
            'total': total,
            'percent': percent,
            'mode': current_mode  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        })







class PicturesView(ListView):
    """ Выводит список всех картинок """
    model = Pictures
    template_name = 'Chem/pictures.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 20



# начало вьюшек раздел реакции с видео

class VideorView(ListView):
    """ Выводит список всех всех реакций с видео """
    model = Videor
    template_name = 'Chem/videors.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(VideorView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class VideorStrView(DetailView):
    model = Videor
    template_name = 'Chem/videorstr.html'
    context_object_name = 'objcontent'


class VideorSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по видеореакциям """

    template_name = 'Chem/videors.html'

    def get_context_data(self, **kwargs):
        context = super(VideorSearchResultView, self).get_context_data(**kwargs)
        searchword = self.request.GET['searchword']
        if self.request.GET['searchword']:
            searchword1 = self.request.GET['searchword'][0].upper() + self.request.GET['searchword'][1:]
        if searchword:
            objects = Videor.objects.\
            filter(Q(title__icontains=searchword)|Q(title__icontains=searchword1)|Q(text__icontains=searchword)|Q(text__icontains=searchword1)).order_by('pk')
            context['objects'] = objects
            context['form'] = SearchForm(initial={'searchword': searchword})
        return context





# начало вьюшек тест реакции неорганики - головы для теста по законам и вопрос-ответ

class ChemTestHeadView(ListView):
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        str_pk = self.kwargs['str']
        
        try:
            reactions = InorganicReaction.objects.filter(number__pk=str_pk)
            a = reactions.first()
            context['numbertitle'] = a.number.title if a else 'Пока нет реакций'
            
            total_db_count = reactions.count()
            context['count'] = total_db_count
            
            # ВСЕГДА генерируем новый тест при заходе на эту страницу
            question_ids = list(reactions.values_list('id', flat=True))
            random.shuffle(question_ids)
            
            if question_ids:
                q1 = question_ids.pop(0)
                context['q1'] = q1
                
                # Записываем свежие данные в сессию, затирая старые
                self.request.session['question_list'] = question_ids
                self.request.session['correct_count'] = 0
                self.request.session['incorrect_count'] = 0
                self.request.session['all_count'] = 0
                
                # Фиксируем общее количество вопросов для счетчика "X из Y"
                self.request.session['total_test_questions'] = total_db_count
            else:
                context['q1'] = 0
                self.request.session['total_test_questions'] = 0
                
        except Exception:
            context['numbertitle'] = 'Ошибка загрузки'
            context['q1'] = 0
        return context

    def get_queryset(self):
        return InorganicReaction.objects.filter(number__pk=self.kwargs['str'])


class ChemMyTestHeadView(ListView):
    template_name = 'Chem/inorganiclawtesthead.html'
    context_object_name = 'objects'

    def get_queryset(self):
        return InorganicReaction.objects.filter(userreaction__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        if queryset.exists():
            context['numbertitle'] = "Мои сохраненные реакции"
            
            total_db_count = queryset.count()
            context['count'] = total_db_count
            
            # ВСЕГДА генерируем новый тест с нуля при заходе на эту страницу
            question_ids = list(queryset.values_list('id', flat=True))
            random.shuffle(question_ids)
            
            if question_ids:
                q1 = question_ids.pop(0)
                context['q1'] = q1
                
                # Полный сброс сессии и запись свежих данных
                self.request.session['question_list'] = question_ids
                self.request.session['correct_count'] = 0
                self.request.session['incorrect_count'] = 0
                self.request.session['all_count'] = 0
                
                # Фиксируем общее количество сохраненных реакций для счетчика "X из Y"
                self.request.session['total_test_questions'] = total_db_count
            else:
                context['q1'] = 0
                self.request.session['total_test_questions'] = 0
        else:
            context['numbertitle'] = 'В вашем списке пока нет реакций'
            context['q1'] = 0
            context['count'] = 0
            self.request.session['total_test_questions'] = 0
            
        return context


class ChemTestQuestionView(TemplateView):
    template_name = 'Chem/inorganiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        qw = InorganicReaction.objects.get(pk=ind)
        context['level'] = qw.level
        
        # Получение имен (Ваш оригинальный код)
        context['name1'] = NamesCompaunds.objects.filter(formula=qw.reagent1).values_list('name', flat=True).first() or ""
        context['name2'] = NamesCompaunds.objects.filter(formula=qw.reagent2).values_list('name', flat=True).first() or ""
        context['name3'] = NamesCompaunds.objects.filter(formula=qw.reagent3).values_list('name', flat=True).first() or ""

        # ИСПРАВЛЕННАЯ ЛОГИКА СЧЕТЧИКА "Х из Y" (1 из 48, 2 из 48 и т.д.)
        total_questions = self.request.session.get('total_test_questions', 0)
        current_num = self.request.session.get('all_count', 0) + 1
        
        # Защита от переполнения счетчика при случайных обновлениях страницы
        if current_num > total_questions and total_questions > 0:
            current_num = total_questions
            
        context['question_progress'] = f"реакция № {current_num} из {total_questions}"
        
        context.update({
            'reagent1': qw.reagent1, 'reagent2': qw.reagent2, 'reagent3': qw.reagent3,
            'condition': qw.condition, 'form': Unswer4Form, 'q1': ind, 'obj': qw,
            'items': self.request.session.get('question_list', []),
            'count': len(self.request.session.get('question_list', []))
        })
        
        # Увеличиваем счетчик общего количества вопросов только после расчета прогресса
        self.request.session['all_count'] = self.request.session.get('all_count', 0) + 1
        return context

    def post(self, request, *args, **kwargs):
        ind = int(self.kwargs['str'])
        qw = InorganicReaction.objects.get(pk=ind)
        
        # Сбор ответов
        answer_list = [request.POST.get(f'field{i}') for i in range(1, 5)]
        answer_list = ["нет" if val in ["not", "ytn", "Ytn", "Not", "Нет"] else (val or "") for val in answer_list]
        
        correct_vals = [qw.product1, qw.product2, qw.product3, qw.product4]
        clean_ans = sorted([w.upper() for w in answer_list if w])
        clean_corr = sorted([w.upper() for w in correct_vals if w])

        if clean_ans == clean_corr:
            messages.success(request, "Верно!" if clean_corr else "нет ответа")
            self.request.session['correct_count'] = self.request.session.get('correct_count', 0) + 1
        else:
            ans_str = " + ".join(filter(None, answer_list))
            messages.success(request, f'Не верно :( .Ваш ответ: = {ans_str}')
            self.request.session['incorrect_count'] = self.request.session.get('incorrect_count', 0) + 1
            
        # ИЗВЛЕКАЕМ СЛЕДУЮЩИЙ ID ЗДЕСЬ
        q_list = self.request.session.get('question_list', [])
        if q_list:
            next_idx = q_list.pop(0)
            self.request.session['next_index'] = next_idx
            self.request.session['question_list'] = q_list
        else:
            self.request.session['next_index'] = None
        
        self.request.session['answer_list'] = answer_list
        return redirect('inorganiclawtestanswer', str=ind)


class ChemTestAnswerView(TemplateView):
    template_name = 'Chem/inorganiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        qw = InorganicReaction.objects.get(pk=ind)
        context['level'] = qw.level
        
        # Заполнение данных реагентов/продуктов и их имен
        formulas = [qw.reagent1, qw.reagent2, qw.reagent3, qw.product1, qw.product2, qw.product3, qw.product4]
        for i, f in enumerate(formulas, 1):
            nm = NamesCompaunds.objects.filter(formula=f).first()
            context[f'name{i}'] = nm.name if nm else ""
            context[f'pkc{i}'] = nm.pk if nm else 1
            if i <= 3: context[f'reagent{i}'] = f
            else: context[f'product{i-3}'] = f

        context['condition'] = qw.condition
        context['obj'] = qw
        context['my_answer'] = self.request.session.get('answer_list', [])
        context['next_index'] = self.request.session.get('next_index')
        
        q_list = self.request.session.get('question_list', [])
        context['items'] = q_list
        context['count'] = len(q_list)

        # ИСПРАВЛЕННАЯ ЛОГИКА СЧЕТЧИКА "Х из Y"
        total_questions = self.request.session.get('total_test_questions', 0)
        current_num = self.request.session.get('all_count', 1)
        context['question_progress'] = f"реакция № {current_num} из {total_questions}"

        # ТОЛЬКО ЭТОТ БЛОК БЫЛ ИЗМЕНЕН ДЛЯ ИСПРАВЛЕНИЯ ПРОЦЕНТОВ
        # Заменяем total_questions - len(q_list) на точное число отвеченных из all_count
        answered_questions = self.request.session.get('all_count', 1)
        cor = self.request.session.get('correct_count', 0)
        context['percent'] = round((cor / answered_questions) * 100) if answered_questions > 0 else 0

        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(UserReaction.objects.filter(user=self.request.user).values_list('reaction_id', flat=True))
        
        return context


# ФУНКЦИИ ИЗБРАННОГО
@login_required
def add_to_list(request, reaction_id):
    if request.method == 'POST':
        reaction = get_object_or_404(InorganicReaction, id=reaction_id)
        UserReaction.objects.get_or_create(user=request.user, reaction=reaction)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def my_favorites_view(request):
    user_items = UserReaction.objects.filter(user=request.user).select_related('reaction')
    return render(request, 'my_list.html', {'user_items': user_items})

def remove_reaction(request, reaction_id):
    if request.method == 'POST':
        UserReaction.objects.filter(user=request.user, reaction_id=reaction_id).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


# конец вьюшек тест реакции неорганики - головы для теста по законам и вопрос-ответ

# ==========================================
# 1. ГОЛОВЫ ТЕСТА (СТАРТОВЫЕ СТРАНИЦЫ И ИНИЦИАЛИЗАЦИЯ)
# ==========================================

class OrganicLawTestHeadView(TemplateView):
    """ Стартовая страница теста по конкретной теме органики. """
    template_name = 'Chem/organiclawtesthead.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num = self.kwargs['num'] 
        topic = get_object_or_404(Organiclaw, pk=num) 
        
        all_reactions = OrganicReaction.objects.filter(number=topic)
        total_db_count = all_reactions.count()
        
        context['count'] = total_db_count
        context['numbertitle'] = topic.title 
        context['obj'] = topic

        question_ids = list(all_reactions.values_list('pk', flat=True))
        random.shuffle(question_ids)
        
        if question_ids:
            q1 = question_ids.pop(0)
            context['q1'] = q1
            
            self.request.session['org_question_list'] = question_ids
            self.request.session['org_next_index'] = q1
            self.request.session['org_all_count'] = 0
            self.request.session['org_correct_count'] = 0
            self.request.session['org_incorrect_count'] = 0
            self.request.session['org_total_test_questions'] = total_db_count
        else:
            context['q1'] = None
            self.request.session['org_total_test_questions'] = 0

        return context


class OrganicFavoritesTestHeadView(LoginRequiredMixin, View):
    """ Инициализация теста по сохраненным реакциям из Избранного пользователя. """
    def get(self, request):
        fav_ids = list(request.user.organic_favorite_reactions.values_list('reaction_id', flat=True))
        total_db_count = len(fav_ids)
        
        if not fav_ids:
            return redirect('organic_my_reactions_list')

        random.shuffle(fav_ids)
        first_id = fav_ids.pop(0)
        
        request.session['org_question_list'] = fav_ids
        request.session['org_next_index'] = first_id
        request.session['org_all_count'] = 0
        request.session['org_correct_count'] = 0
        request.session['org_incorrect_count'] = 0
        request.session['org_total_test_questions'] = total_db_count
        
        return redirect('organiclawtestquestion', str=first_id)


# ==========================================
# 2. СТРАНИЦА ВОПРОСА (ОТОБРАЖЕНИЕ И ПРОВЕРКА ОТВЕТА)
# ==========================================

class OrganicChemTestQuestionView(TemplateView):
    """ Выводит вопрос теста — только текст реакции и поля для ввода """
    template_name = 'Chem/organiclawtestquestion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
        total_questions = self.request.session.get('org_total_test_questions', 0)
        current_num = self.request.session.get('org_all_count', 0) + 1
        
        if current_num > total_questions and total_questions > 0:
            current_num = total_questions
            
        context['question_progress'] = f"реакция № {current_num} из {total_questions}"
        context['level'] = qw.level

        # --- ВОТ ЭТОТ КРИТИЧЕСКИЙ БЛОК МЫ ДОБАВИЛИ ДЛЯ ПОИСКА SMILES ---
        # Собираем только реагенты (первые 3 элемента)
        reagent_list = [qw.reagent1, qw.reagent2, qw.reagent3]
        for i, val in enumerate(reagent_list, 1):
            if val:
                target = str(val).strip()
                # Ищем структуру в базе, используя полный менеджер all_objects
                found_obj = OrganicNames.all_objects.filter(molecule_short__iexact=target).first()
                context[f'obj_n{i}'] = found_obj
            else:
                context[f'obj_n{i}'] = None
        # --------------------------------------------------------------

        context.update({
            'reagent1': qw.reagent1,
            'reagent2': qw.reagent2,
            'reagent3': qw.reagent3,
            'condition': qw.condition,
            'form': OrganicTestForm(), 
            'q1': ind,
            'obj': qw,
            'items': self.request.session.get('org_question_list', []),
            'count': len(self.request.session.get('org_question_list', []))
        })
        
        return context


    def post(self, request, *args, **kwargs):
        ind = int(self.kwargs['str'])
        qw = get_object_or_404(OrganicReaction, pk=ind)
        
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

        correct_answers = [qw.product1, qw.product2, qw.product3, qw.product4]
        correct_list = [str(c).strip() for c in correct_answers if c]
        
        user_upper = sorted([a.upper() for a in user_answers])
        correct_upper = sorted([c.upper() for c in correct_list])

        # Проверяем, ввел ли пользователь вообще хоть что-то
        if len(user_answers) == 0:
            request.session['org_has_answer'] = False
            request.session['org_is_correct'] = False
            request.session['org_incorrect_count'] = request.session.get('org_incorrect_count', 0) + 1
        else:
            request.session['org_has_answer'] = True
            if user_upper == correct_upper:
                # Убрали messages.success, пишем только в сессию
                request.session['org_is_correct'] = True
                request.session['org_correct_count'] = request.session.get('org_correct_count', 0) + 1
            else:
                # Убрали messages.error, пишем только в сессию
                request.session['org_is_correct'] = False
                request.session['org_incorrect_count'] = request.session.get('org_incorrect_count', 0) + 1

        request.session['org_all_count'] = request.session.get('org_all_count', 0) + 1

        # Сохраняем списки ответов для отображения на странице результатов
        request.session['org_last_user_answers'] = user_answers
        request.session['org_last_correct_answers'] = correct_list

        question_list = request.session.get('org_question_list', [])
        if question_list:
            next_index = question_list.pop(0)
            request.session['org_next_index'] = next_index
            request.session['org_question_list'] = question_list
        else:
            request.session['org_next_index'] = None
            
        return redirect('organiclawtestanswer', str=ind)


# ==========================================
# 3. СТРАНИЦА ОТВЕТА (РЕЗУЛЬТАТЫ, СТРУКТУРНЫЕ ФОРМУЛЫ SMILES)
# ==========================================

class OrganicChemTestAnswerView(TemplateView):
    """ Показывает правильный ответ, процент успеха, названия веществ и их SMILES """
    template_name = 'Chem/organiclawtestanswer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs.get('str')
        
        qw = get_object_or_404(OrganicReaction, pk=ind)
        context['obj'] = qw
        context['level'] = qw.level

        # Поиск связанных соединений (Имена и SMILES) в OrganicNames
        struct_list = [
            qw.reagent1, qw.reagent2, qw.reagent3, 
            qw.product1, qw.product2, qw.product3, qw.product4
        ]
        
        for i, val in enumerate(struct_list, 1):
            if val:
                target = str(val).strip()
                found_obj = OrganicNames.objects.filter(molecule_short__iexact=target).first()
                context[f'obj_n{i}'] = found_obj
            else:
                context[f'obj_n{i}'] = None

        # Проверка Избранного для текущего пользователя
        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(
                OrganicUserReaction.objects.filter(user=self.request.user)
                .values_list('reaction_id', flat=True)
            )
        else:
            context['favorite_ids'] = []

        # Расчет статистики и получение прогресса
        all_c = self.request.session.get('org_all_count', 0) or 0
        corr_c = self.request.session.get('org_correct_count', 0) or 0
        context['percent'] = round((corr_c / all_c) * 100) if all_c > 0 else 0
        
        total_questions = self.request.session.get('org_total_test_questions', 0)
        current_num = all_c if all_c > 0 else 1
        context['question_progress'] = f"реакция № {current_num} из {total_questions}"
        
        # Получение данных очереди теста без удаления (безопасно при F5)
        next_id = self.request.session.get('org_next_index')
        q_list = self.request.session.get('org_question_list', [])
        
        context['next_index'] = next_id
        context['items'] = q_list
        context['count'] = len(q_list)
            
        return context


# ==========================================
# 4. ФУНКЦИИ ИЗБРАННОГО (ДОБАВЛЕНИЕ, УДАЛЕНИЕ, СПИСОК)
# ==========================================

def organic_add_to_list(request, reaction_id):
    """ Добавление органической реакции в список пользователя """
    if request.user.is_authenticated:
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
    """ Выводит страницу со списком всех избранных реакций текущего пользователя """
    my_reactions = OrganicUserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'Chem/organic_my_list.html', {
        'my_reactions': my_reactions
    })

# конец вьюшек тест - реакции органики - головы для теста по законам и вопрос-ответ





@login_required
def my_reactions_list(request):
    # Получаем все связи текущего пользователя с реакциями
    # select_related('reaction') подгрузит данные InorganicReaction одним запросом
    user_items = UserReaction.objects.filter(user=request.user).select_related('reaction')
    
    return render(request, 'Chem/my_reactions.html', {'user_items': user_items})














# справочные страницы:таблицы, ссылки, заглавная страница
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

#конец  справочные страницы:таблицы, ссылки, заглавная страница


#законы химии общие, органика, неорганика: главная, поиск, персональная и еще тест по общей химии, и списка веществ орг,неорг с поиском


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

    def get_context_data(self, **kwargs):
        context = super(InorganiclawStrView, self).get_context_data(**kwargs)
        
        # Используем get_object_or_404, чтобы вместо ошибки сервера отдавать красивую страницу 404
        # Также добавляем select_related/prefetch_related для реакций и связанных материалов, если нужно
        obj = get_object_or_404(Inorganiclaw, pk=self.kwargs.get("pk"))
        
        # Получаем реакции, связанные с этим законом
        qw = InorganicReaction.objects.filter(number=obj)
        
        context['obj'] = obj
        context['qw'] = qw
        return context


class ChemSearchResultView(TemplateView):
    """ Представление, которое выводит результаты поиска по законам неорганической химии """

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







class CompaundStrView(TemplateView):
    """страница неорганического соединения"""
    template_name = 'Chem/compaund.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        objcontent = NamesCompaunds.objects.get(pk=ind) 
        f = objcontent.formula
        context['objcontent'] = objcontent

        # АВТОМАТИЧЕСКИЙ ПЕРЕНОС ПРИ НАЛИЧИИ ССЫЛОК
        has_main_video = objcontent.video and objcontent.video.strip() not in ["", "-", "—"]
        has_extra_links = objcontent.extra_videos.exists()

        if (has_main_video or has_extra_links) and not objcontent.is_interesting:
            objcontent.is_interesting = True
            objcontent.save(update_fields=['is_interesting'])

        # ПОЛУЧЕНИЕ РЕАКЦИЙ С УЧАСТИЕМ СОЕДИНЕНИЯ
        qw = InorganicReaction.objects.filter(
            Q(reagent1__icontains=f) | Q(reagent2__icontains=f) | Q(reagent3__icontains=f) |
            Q(product1__icontains=f) | Q(product2__icontains=f) | Q(product3__icontains=f) | Q(product4__icontains=f)
        )
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

    def get_context_data(self, **kwargs):
        context = super(AtomlawStrView, self).get_context_data(**kwargs)
        
        # Загружаем объект закона общей химии
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
    """ Выводит список неорганических веществ без инструкции """
    model = NamesCompaunds
    template_name = 'Chem/compaunds.html'
    context_object_name = 'objects'
    ordering = ['pk']
    paginate_by = 6

    def get_queryset(self):
        # Получаем базовый список и сразу исключаем вещество с названием "инструкция вещество"
        queryset = super().get_queryset().exclude(name__iexact='инструкция')
        
        # Проверяем фильтр «интересных» веществ
        show_filter = self.request.GET.get('filter')
        if show_filter == 'interesting':
            return queryset.filter(is_interesting=True)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['current_filter'] = self.request.GET.get('filter', 'all')
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

    def get_context_data(self, **kwargs):
        context = super(OrganiclawStrView, self).get_context_data(**kwargs)
        
        # Загружаем объект закона органической химии
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
    """страница органического соединения"""
    template_name = 'Chem/organiccompaund.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ind = self.kwargs['str']
        objcontent = OrganicNames.objects.get(pk=ind) 
        f = objcontent.name1
        context['objcontent'] = objcontent

        # АВТОМАТИЧЕСКИЙ ПЕРЕНОС ПРИ НАЛИЧИИ ССЫЛОК
        has_main_video = objcontent.video and objcontent.video.strip() not in ["", "-", "—"]
        has_extra_links = objcontent.extra_videos.exists()

        if (has_main_video or has_extra_links) and not objcontent.is_interesting:
            objcontent.is_interesting = True
            objcontent.save(update_fields=['is_interesting'])

        # ПОЛУЧЕНИЕ РЕАКЦИЙ С УЧАСТИЕМ СОЕДИНЕНИЯ
        qw = OrganicReaction.objects.filter(
            Q(reagent1__icontains=f) | Q(reagent2__icontains=f) | Q(reagent3__icontains=f) | 
            Q(product1__icontains=f) | Q(product2__icontains=f) | Q(product3__icontains=f) | Q(product4__icontains=f)
        )
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


# === МОБИЛЬНОЕ ПРИЛОЖЕНИЕ ===
import random
from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rdkit import Chem  # Если используется Chemredkit, замените импорт или используйте его ниже



@api_view(['GET'])
@permission_classes([AllowAny])
def get_chemistry_meta(request):
    """
    Отдает мобильному приложению справочную информацию 
    для построения экрана выбора категорий теста.
    """
    return Response({
        "organic_groups": ORGANIC_GROUPS,
        "general_formulas": CLASS_GENERAL_FORMULAS
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_start_test(request):
    """
    Генерирует сбалансированный тест из 10 вопросов на основе 
    выбранного режима и групп веществ, без использования сессий.
    """
    mode = request.data.get('mode', 'name_to_mol')
    selected_group_names = request.data.get('selected_groups', [])

    # 1. Раскрываем выбранные ГРУППЫ в плоский список КЛАССОВ
    selected_classes = []
    for group in ORGANIC_GROUPS:
        if mode == 'form_to_class' or group['name'] in selected_group_names or not selected_group_names:
            selected_classes.extend(group['classes'])

    # 2. Ограничение для школьного режима "Формула -> Класс"
    if mode == 'form_to_class':
        allowed_keys = [
            'alkanes', 'alkenes', 'alkynes', 'alkadienes', 'cycloalkanes', 'alcohols', 'ethers', 
            'aldehydes', 'ketones', 'saturated_monobasic_carboxylic_acids', 'esters', 'amino_acids', 
            'diols', 'triols', 'phenols', 'primary_amines', 'secondary_amines', 'tertiary_amines', 
            'Ароматические амины', 'halogen_derivatives'
        ]
        selected_classes = [c for c in selected_classes if c in allowed_keys]

    # 3. Фильтруем базовый QuerySet по режимам
    queryset = OrganicNames.objects.all()
    if mode == 'name_to_mol':
        queryset = queryset.filter(test_name_to_structure=True)
    elif mode == 'mol_to_name':
        queryset = queryset.filter(test_structure_to_name=True)
    elif mode == 'form_to_class':
        queryset = queryset.filter(test_formula_to_class=True).exclude(formula__isnull=True).exclude(formula__exact='')

    # 4. Система интервального повторения (если пользователь авторизован)
    if request.user.is_authenticated:
        UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).update(
            skip_count=F('skip_count') - 1
        )
        skipped_ids = UserQuestionProgress.objects.filter(user=request.user, skip_count__gt=0).values_list('question_id', flat=True)
        queryset_filtered = queryset.exclude(id__in=skipped_ids)
        if queryset_filtered.count() >= 10:
            queryset = queryset_filtered

    # 5. Оптимизированная выборка ID и группировка по классам
    raw_questions = queryset.filter(organic_class__in=selected_classes).values('id', 'organic_class')
    
    class_pools = {}
    for q in raw_questions:
        class_pools.setdefault(q['organic_class'], []).append(q['id'])
        
    for c_slug in class_pools:
        random.shuffle(class_pools[c_slug])

    # 6. Алгоритм фиксированной длины теста с перемешиванием классов
    final_ids = []
    target_questions_count = 10
    active_slugs = list(class_pools.keys())
    random.shuffle(active_slugs)

    while len(final_ids) < target_questions_count and active_slugs:
        for c_slug in list(active_slugs):
            if class_pools[c_slug]:
                q_id = class_pools[c_slug].pop(0)
                final_ids.append(q_id)
                if len(final_ids) == target_questions_count:
                    break
            else:
                active_slugs.remove(c_slug)
                
    random.shuffle(final_ids)

    if not final_ids:
        return Response({"error": "По вашему запросу вопросы не найдены"}, status=404)

    # 7. Извлечение полных данных карточек и генерация "умных" вариантов ответов
    substances = OrganicNames.objects.filter(id__in=final_ids)
    substances_ordered = sorted(substances, key=lambda obj: final_ids.index(obj.id))
    classes_dict = dict(ORGANIC_CLASSES)

    questions_data = []
    for sub in substances_ordered:
        names = [n for n in [sub.name1, sub.name2, sub.name3, sub.name4] if n]
        display_name = random.choice(names) if names else sub.name1
        
        options = []
        if mode == 'form_to_class':
            current_class = sub.organic_class
            options.append(current_class)
            
            isomer_class = CLASS_ISOMERS.get(current_class)
            if isomer_class and isomer_class in selected_classes:
                options.append(isomer_class)

            remaining_classes = [c for c in selected_classes if c not in options]
            random.shuffle(remaining_classes)
            while len(options) < 4 and remaining_classes:
                options.append(remaining_classes.pop(0))

            random.shuffle(options)
            options = [{"slug": opt, "label": classes_dict.get(opt, opt)} for opt in options]

        questions_data.append({
            "id": sub.id,
            "display_name": display_name,
            "organic_class": sub.organic_class,
            "formula": sub.formula,
            "molecule_smiles": sub.molecule,
            "options": options
        })

    return Response({
        "mode": mode,
        "total_questions": len(questions_data),
        "questions": questions_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_check_answer(request):
    """
    Принимает ответ от mobile-приложения, сверяет его по логике бэкенда,
    фиксирует интервальное повторение и возвращает полный разбор результата.
    """
    question_id = request.data.get('id')
    mode = request.data.get('mode', 'name_to_mol')
    user_ans = str(request.data.get('user_answer', '')).strip()

    if not question_id:
        return Response({"error": "Не передан id вопроса"}, status=400)

    try:
        obj = OrganicNames.objects.get(id=question_id)
        is_correct = False
        both_answers_text = ""
        general_formula = ""
        classes_dict = dict(ORGANIC_CLASSES)

        # 1. РЕЖИМ: НАЗВАНИЕ -> СТРУКТУРА (Проверка графа RDKit)
        if mode == 'name_to_mol':
            m1 = Chem.MolFromSmiles(user_ans)
            m2 = obj.mol_object  # Используем ваше свойство mol_object из модели
            if m1 and m2:
                is_correct = Chem.MolToSmiles(m1) == Chem.MolToSmiles(m2)
            else:
                return Response({
                    "is_correct": False, 
                    "error": "Не удалось распознать структуру молекулы. Проверьте валентности атомов."
                })

        # 2. РЕЖИМ: СТРУКТУРА -> НАЗВАНИЕ (Текстовый ввод названия)
        elif mode == 'mol_to_name':
            valid_names = [name.strip().lower() for name in [obj.name1, obj.name2, obj.name3, obj.name4] if name]
            is_correct = user_ans.lower() in valid_names

        # 3. РЕЖИМ: ФОРМУЛА -> КЛАСС (Выбор класса с учетом межклассовых изомеров)
        elif mode == 'form_to_class':
            correct_class = obj.organic_class
            isomer_class = CLASS_ISOMERS.get(correct_class)
            
            correct_label = classes_dict.get(correct_class, "Неизвестный класс")
            isomer_label = classes_dict.get(isomer_class, "")

            general_formula = CLASS_GENERAL_FORMULAS.get(correct_class, "")

            if user_ans == correct_class or (isomer_class and user_ans == isomer_class):
                is_correct = True

            if isomer_label:
                both_answers_text = f"У данных классов одинаковая брутто-формула. Верны оба ответа: {correct_label} и {isomer_label}."

        # === ФИКСАЦИЯ ПРОГРЕССА ИНТЕРВАЛЬНОГО ПОВТОРЕНИЯ ===
        if request.user.is_authenticated:
            progress, created = UserQuestionProgress.objects.get_or_create(
                user=request.user, question=obj
            )
            progress.skip_count = 30 if is_correct else 0
            progress.save()

        # Собираем строку всех правильных названий для вывода работы над ошибками
        names_list = [name.strip() for name in [obj.name1, obj.name2, obj.name3, obj.name4] if name and str(name).strip()]
        all_names_string = ", ".join(names_list) if names_list else "Название отсутствует"

        return Response({
            "is_correct": is_correct,
            "correct_class_slug": obj.organic_class,
            "correct_class_label": classes_dict.get(obj.organic_class, ""),
            "all_correct_names": all_names_string,
            "true_smiles": obj.molecule,
            "general_formula": general_formula,
            "both_answers_text": both_answers_text,
        })

    except OrganicNames.DoesNotExist:
        return Response({"error": "Вещество не найдено в базе данных"}, status=404)
# === КОНЕЦ БЛОКА МОБИЛЬНОЕ ПРИЛОЖЕНИЕ ===



