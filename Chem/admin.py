from django import forms
from django.contrib import admin
from django.contrib import messages
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget
import tablib

from ckeditor_uploader.widgets import CKEditorUploadingWidget
# from .widgets import JSMEWidget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

# видеореакции классы для отображения в админке

# класс для загрузки/выгрузки видеореакции
class VideorResource(resources.ModelResource):
    class Meta:
        model = Videor
        skip_unchanged = True
        report_skipped = True 


# класс добавления стилей к окну видеореакции
class VideorAdminForm(forms.ModelForm):
    text = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = Videor
        fields = '__all__'
        
# класс подробностей видеореакции   
class VideorAdmin(ImportExportActionModelAdmin):
    resource_class = VideorResource
    form = VideorAdminForm
    search_fields = ['pk', 'title', 'text'] 
    save_as = True
    list_display = ('pk', 'title')
    
        
# фиксация формы в админке видеореакции
admin.site.register(Videor, VideorAdmin)

# окончание видеореакции


                    
class JSMEWidget(forms.Widget):
    template_name = 'admin/widgets/jsme_editor.html'
    
    def render(self, name, value, attrs=None, renderer=None):
        value = value or ""
        final_attrs = self.build_attrs(attrs)
        id_name = final_attrs.get('id', 'id_molecule')
        
        html = f"""
        <div class="jsme-admin-wrapper" style="margin-bottom: 20px;">
            <div style="margin-bottom: 10px;">
                <label style="font-weight: bold;">SMILES строка:</label>
                <input type="text" name="{name}" id="{id_name}" value='{value}' style="width: 100%; font-family: monospace; padding: 8px; border: 1px solid #ccc;">
            </div>
            <div id="jsme_container_{id_name}" style="width: 500px; height: 350px; border: 1px solid #999; background: #fff;"></div>
        </div>
        <script type="text/javascript" src="/static/jsme/jsme.nocache.js"></script>
        <script type="text/javascript">
            function startJSME_{id_name.replace('-', '_')}() {{
                var field = document.getElementById("{id_name}");
                var applet = new JSApplet.JSME("jsme_container_{id_name}", "500px", "350px", {{ "options": "oldLook,paste,autocenter" }});
                if (field.value) applet.readGenericMolecularInput(field.value);
                applet.setCallBack("AfterStructureModified", function(event) {{
                    field.value = event.src.smiles();
                }});
                field.addEventListener('input', function() {{
                    try {{ applet.readGenericMolecularInput(this.value); }} catch (e) {{}}
                }});
            }}
            window.jsmeOnLoad = startJSME_{id_name.replace('-', '_')};
            setTimeout(function() {{
                if (typeof JSApplet !== 'undefined') startJSME_{id_name.replace('-', '_')}();
            }}, 1000);
        </script>
        """
        return mark_safe(html)

# 1. Форма для админки
class OrganicNamesAdminForm(forms.ModelForm):
    class Meta:
        model = OrganicNames
        fields = '__all__'
        widgets = {
            'molecule': JSMEWidget(),
            'appearance': CKEditorUploadingWidget(),
        }

# 2. Фильтр для поиска записей с пустым полем organic_class
class OrganicClassEmptyFilter(admin.SimpleListFilter):
    title = 'Наличие класса (organic_class)'
    parameter_name = 'empty_class'
    
    def lookups(self, request, model_admin):
        return (
            ('empty', 'Не заполнено'),
            ('filled', 'Заполнено'),
        )
        
    def queryset(self, request, queryset):
        if self.value() == 'empty':
            return queryset.filter(organic_class__isnull=True) | queryset.filter(organic_class='')
        if self.value() == 'filled':
            return queryset.exclude(organic_class__isnull=True).exclude(organic_class='')
        return queryset

# 3. Основной класс админки
@admin.register(OrganicNames)
class OrganicNamesAdmin(admin.ModelAdmin):
    form = OrganicNamesAdminForm
    search_fields = ['name1', 'name2', 'name3', 'formula'] 
    
    list_display = (
        'pk', 'name1', 'molecule_short', 'organic_class', 
        'is_interesting', 'test_name_to_structure', 
        'test_structure_to_name', 'test_formula_to_class'
    )
    
    list_editable = (
        'is_interesting', 'test_name_to_structure', 
        'test_structure_to_name', 'test_formula_to_class'
    )
    
    list_filter = (
        OrganicClassEmptyFilter, 'organic_class', 'is_interesting',
        'test_name_to_structure', 'test_structure_to_name', 'test_formula_to_class'
    )

    # ВСТАВЬТЕ ЭТОТ БЛОК внутрь класса OrganicNamesAdmin:
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        # Если не хотите создавать отдельный файл, можно внедрить стили прямо через JavaScript инлайново:
        js = ('data:text/javascript,document.head.insertAdjacentHTML("beforeend", "<style>.results table th .text a { white-space: normal !important; display: block; min-width: 120px; }</style>");',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            msg = f"Редактирована запись № {obj.pk}"
        else:
            msg = f"Создана запись № {obj.pk}"
        messages.success(request, msg)
        
# знх классы для отображения в админке

# класс для загрузки/выгрузки знх
class InorganiclawResource(resources.ModelResource):
    class Meta:
        model = Inorganiclaw
        


# класс добавления стилей к окну знх
class InorganiclawAdminForm(forms.ModelForm):
    title = forms.CharField(label="Заголовок", widget=CKEditorUploadingWidget())
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())
    formula = forms.CharField(label="Общая формула закона", widget=CKEditorUploadingWidget())
    examples = forms.CharField(label="Примеры", widget=CKEditorUploadingWidget())
    exceptions = forms.CharField(label="Исключения", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = Inorganiclaw
        fields = '__all__'
        
# класс подробностей знх   
class InorganiclawAdmin(ImportExportActionModelAdmin):
    resource_class = InorganiclawResource
    list_display = ('number', 'title' , 'display_count', 'pk')
    ordering = ('number',)
    search_fields = ['number', 'title', 'text', 'keywords']
    form = InorganiclawAdminForm
    save_as = True

    def display_count(self, obj):
        return obj.inorganicreaction_set.count()
    
    display_count.short_description = "реакций"
        
# фиксация формы в админке знх
admin.site.register(Inorganiclaw, InorganiclawAdmin)





# 1. Класс для загрузки/выгрузки реакции
class InorganicReactionResource(resources.ModelResource):
    class Meta:
        model = InorganicReaction
        skip_unchanged = True
        report_skipped = True   


# 2. Класс добавления стилей к окну реакции (CKEditor)
class InorganicReactionAdminForm(forms.ModelForm):
    extra = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = InorganicReaction
        fields = '__all__'
        

# 3. Основной класс админки реакции   
class InorganicReactionAdmin(ImportExportActionModelAdmin):
    resource_class = InorganicReactionResource
    form = InorganicReactionAdminForm
    autocomplete_fields = ['number']
    
    # Добавили 'level' в список отображения, чтобы сразу видеть результат
    list_display = ('pk', 'metatitle', 'level') 
    search_fields = ['pk', 'reagent1', 'reagent2', 'metatitle'] 
    save_as = True

    # Регистрируем ДВА отдельных действия в выпадающем меню списка
    actions = ['mass_set_level_oge', 'mass_set_level_ege']

    # Действие №1: Мгновенная установка уровня ОГЭ
    @admin.action(description='Установить уровень "ОГЭ" для выбранных реакций')
    def mass_set_level_oge(self, request, queryset):
        updated_count = queryset.update(level='ОГЭ') 
        self.message_user(
            request, 
            f'Успешно установлен уровень "ОГЭ" для {updated_count} реакций.', 
            messages.SUCCESS
        )

    # Действие №2: Мгновенная установка уровня ЕГЭ
    @admin.action(description='Установить уровень "ЕГЭ" для выбранных реакций')
    def mass_set_level_ege(self, request, queryset):
        updated_count = queryset.update(level='ЕГЭ') 
        self.message_user(
            request, 
            f'Успешно установлен уровень "ЕГЭ" для {updated_count} реакций.', 
            messages.SUCCESS
        )

    # Ваш оригинальный метод сохранения с валидацией веществ
    def save_model(self, request, obj, form, change):
        # 1. Проверка наличия веществ в модели названий
        items_to_check = [
            obj.reagent1, obj.reagent2, obj.reagent3, 
            obj.product1, obj.product2, obj.product3, obj.product4
        ]
        
        for item in items_to_check:
            if item is not None and item != "" and not NamesCompaunds.objects.filter(formula=item).exists():
                messages.warning(request, f"Внимание: вещества '{item}' нет в модели названий.")

        # 2. Выполняем сохранение объекта
        super().save_model(request, obj, form, change)

        # 3. Вывод сообщения о редактировании/создании с PK
        if change:
            messages.success(request, f"Редактирована запись № {obj.pk}")
        else:
            messages.success(request, f"Создана новая запись № {obj.pk}")


# 4. Фиксация формы в админке реакции
admin.site.register(InorganicReaction, InorganicReactionAdmin)

# вещества классы для отображения в админке
# класс для загрузки/выгрузки вещества
class NamesCompaundsResource(resources.ModelResource):
    class Meta:
        model = NamesCompaunds
        skip_unchanged = True
        report_skipped = True

# класс добавления стилей к окну вещества
class NamesCompaundsAdminForm(forms.ModelForm):
    appearance = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)
    class Meta:
        model = NamesCompaunds
        fields = '__all__'

# класс подробностей вещества
class NamesCompaundsAdmin(ImportExportActionModelAdmin):
    resource_class = NamesCompaundsResource
    form = NamesCompaundsAdminForm
    search_fields = ['pk', 'formula', 'name']
    save_as = True
    
    # Выводим галочку в таблицу
    list_display = ('pk', 'formula', 'name', 'is_interesting')
    
    # Позволяет отмечать интересные вещества прямо из списка
    list_editable = ('is_interesting',)
    
    # Фильтр справа только по этому полю
    list_filter = ('is_interesting',)

# фиксация формы в админке вещества
admin.site.register(NamesCompaunds, NamesCompaundsAdmin)


# законы строения атомов классы для отображения в админке

# класс для загрузки/выгрузки законы строения атомов
class AtomlawResource(resources.ModelResource):
    class Meta:
        model = Atomlaw
        skip_unchanged = True
        report_skipped = True 


# класс добавления стилей к окну законы строения атомов
class AtomlawAdminForm(forms.ModelForm):
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())

    class Meta:
        model = Atomlaw
        fields = '__all__'
        
# класс подробностей законы строения атомов   
class AtomlawAdmin(ImportExportActionModelAdmin):
    resource_class = AtomlawResource
    form = AtomlawAdminForm
    search_fields = ['pk', 'title', 'text'] 
    save_as = True
    list_display = ('pk', 'title')
    
        
# фиксация формы в админке законы строения атомов
admin.site.register(Atomlaw, AtomlawAdmin)

# тесты атомов классы для отображения в админке

# класс для загрузки/выгрузки тесты атомов
class AtomTestResource(resources.ModelResource):
    class Meta:
        model = AtomTest
        skip_unchanged = True
        report_skipped = True 


# класс добавления стилей к окну тесты атомов
class AtomTestAdminForm(forms.ModelForm):
    text = forms.CharField(label="Вопрос", widget=CKEditorUploadingWidget(), required=False)
    answer = forms.CharField(label="Ответ", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = AtomTest
        fields = '__all__'
        
# класс подробностей тесты атомов   
class AtomTestAdmin(ImportExportActionModelAdmin):
    resource_class = AtomTestResource
    form = AtomTestAdminForm
    search_fields = ['pk', 'text'] 
    save_as = True
    list_display = ('pk', 'text')
    
        
# фиксация формы в админке тесты атомов
admin.site.register(AtomTest, AtomTestAdmin)



admin.site.register(Table)
admin.site.register(Link)




from django.contrib import admin
from django import forms
from .models import OrganicNames
from .widgets import JSMEWidget

# # 1. Создаем форму, которая подменит стандартное поле на редактор JSME
# class OrganicNamesAdminForm(forms.ModelForm):
#     class Meta:
#         model = OrganicNames
#         fields = '__all__'
#         widgets = {
#             # Указываем, что для поля 'molecule' используем наш JSMEWidget
#             'molecule': JSMEWidget(), 
#         }

# # 2. Регистрируем модель в админке с использованием этой формы
# @admin.register(OrganicNames)
# class OrganicNamesAdmin(admin.ModelAdmin):
#     form = OrganicNamesAdminForm
#     # Отображаем имя и SMILES-строку в списке всех записей
#     list_display = ('name1', 'molecule')




# базовая органика
# зох классы для отображения в админке

# класс для загрузки/выгрузки зох
class OrganiclawResource(resources.ModelResource):
    class Meta:
        model = Organiclaw
        


# класс добавления стилей к окну # класс для загрузки/выгрузки зох
class OrganiclawAdminForm(forms.ModelForm):
    title = forms.CharField(label="Заголовок", widget=CKEditorUploadingWidget())
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())
    exceptions = forms.CharField(label="Исключения", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = Organiclaw
        fields = '__all__'
        
# класс подробностей # класс для загрузки/выгрузки зох   
class OrganiclawAdmin(ImportExportActionModelAdmin):
    resource_class = OrganiclawResource
    list_display = ('number', 'title' , 'display_count', 'pk')
    ordering = ('number',)
    search_fields = ['number', 'title', 'text', 'keywords']
    form = OrganiclawAdminForm
    save_as = True

    def display_count(self, obj):
        return obj.organicreaction_set.count()
    
    display_count.short_description = "реакций"
        
# фиксация формы в админке # класс для загрузки/выгрузки зох
admin.site.register(Organiclaw, OrganiclawAdmin)





# реакции ох классы для отображения в админке

# класс для загрузки/выгрузки реакции ох
class OrganicReactionResource(resources.ModelResource):
    class Meta:
        model = OrganicReaction
        skip_unchanged = True
        report_skipped = True   


# класс добавления стилей к окну реакции ох
class OrganicReactionAdminForm(forms.ModelForm):
    extra = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = OrganicReaction
        fields = '__all__'
        
# класс подробностей реакции ох   
class OrganicReactionAdmin(ImportExportActionModelAdmin):
    resource_class = OrganicReactionResource
    form = OrganicReactionAdminForm
    autocomplete_fields = ['number']
    list_display = ('pk', 'metatitle')
    search_fields = ['pk', 'reagent1', 'reagent2', 'metatitle'] 
    save_as = True

    def save_model(self, request, obj, form, change):
        # Собираем все значения реагентов и продуктов
        check_values = [
            obj.reagent1, obj.reagent2, obj.reagent3,
            obj.product1, obj.product2, obj.product3, obj.product4
        ]

        # Убираем None, пустые строки и дубликаты
        names_to_verify = {name for name in check_values if name}

        if names_to_verify:
            # Ищем существующие значения в поле molecule_short одним запросом
            existing_names = set(
                OrganicNames.objects.filter(molecule_short__in=names_to_verify)
                .values_list('molecule_short', flat=True)
            )

            # Находим разницу: те, что ввели, но которых нет в базе
            missing_names = names_to_verify - existing_names

            for name in missing_names:
                messages.warning(request, f"Внимание: вещества '{name}' нет в модели названий (поле molecule_short).")

        super().save_model(request, obj, form, change)
        
# фиксация формы в админке реакции ох
admin.site.register(OrganicReaction, OrganicReactionAdmin)


admin.site.register(Pictures)

