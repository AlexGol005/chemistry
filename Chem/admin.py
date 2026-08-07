from django import forms
from django.contrib import admin
from django.contrib import messages
from .models import (
    Atomlaw, AtomlawImage, AtomlawVideo, AtomlawPresentation,
    Inorganiclaw, InorganiclawImage, InorganiclawVideo, InorganiclawPresentation,
    Organiclaw, OrganiclawImage, OrganiclawVideo, OrganiclawPresentation
)
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
        # Если значение None, заменяем на пустую строку
        value = value or ""
        final_attrs = self.build_attrs(attrs)
        id_name = final_attrs.get('id', 'id_molecule')
        
        # Мы вставляем HTML напрямую, чтобы избежать ошибок поиска шаблона в циклах
        html = f"""
        <div class="jsme-admin-wrapper" style="margin-bottom: 20px;">
            <div style="margin-bottom: 10px;">
                <label style="font-weight: bold;">SMILES строка:</label>
                <input type="text" name="{name}" id="{id_name}" value='{value}' 
                       style="width: 100%; font-family: monospace; padding: 8px; border: 1px solid #ccc;">
            </div>
            <div id="jsme_container_{id_name}" style="width: 500px; height: 350px; border: 1px solid #999; background: #fff;"></div>
        </div>
        <script type="text/javascript" src="/static/jsme/jsme.nocache.js"></script>
        <script type="text/javascript">
            function startJSME_{id_name.replace('-', '_')}() {{
                var field = document.getElementById("{id_name}");
                var applet = new JSApplet.JSME("jsme_container_{id_name}", "500px", "350px", {{
                    "options": "oldLook,paste,autocenter"
                }});
                if (field.value) applet.readGenericMolecularInput(field.value);
                applet.setCallBack("AfterStructureModified", function(event) {{
                    field.value = event.src.smiles();
                }});
                field.addEventListener('input', function() {{
                    try {{ applet.readGenericMolecularInput(this.value); }} catch (e) {{}}
                }});
            }}
            window.jsmeOnLoad = startJSME_{id_name.replace('-', '_')};
            setTimeout(function() {{ if (typeof JSApplet !== 'undefined') startJSME_{id_name.replace('-', '_')}(); }}, 1000);
        </script>
        """
        return mark_safe(html)


# органические соединения органические вещества


# === 1. ФОРМА ДЛЯ АДМИНКИ ===
class OrganicNamesAdminForm(forms.ModelForm):
    class Meta:
        model = OrganicNames
        fields = '__all__'
        widgets = {
            'molecule': JSMEWidget(),
            'appearance': CKEditorUploadingWidget(),
        }


# === 2. ФИЛЬТР ПО КОНКРЕТНЫМ КЛАССАМ (С КРАСИВЫМИ НАЗВАНИЯМИ) ===
class OrganicClassChoicesFilter(admin.SimpleListFilter):
    title = 'Класс органики'  # Заголовок блока в правой панели
    parameter_name = 'class_slug'

    def lookups(self, request, model_admin):
        # Используем ваш глобальный список ORGANIC_CLASSES (кортежи вида: ('slug', 'Название'))
        # Если в базе есть записи, фильтр покажет их понятные русские имена
        return ORGANIC_CLASSES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organic_class=self.value())
        return queryset


# === 3. ФИЛЬТР ДЛЯ ПОИСКА ЗАПИСЕЙ С ПУСТЫМ ПОЛЕМ ORGANIC_CLASS ===
class OrganicClassEmptyFilter(admin.SimpleListFilter):
    title = 'Наличие класса (organic_class)'  # Заголовок в правой панели
    parameter_name = 'empty_class'

    def lookups(self, request, model_admin):
        return (
            ('empty', 'Не заполнено'),
            ('filled', 'Заполнено'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'empty':
            # Фильтруем и NULL, и пустые строки
            return queryset.filter(organic_class__isnull=True) | queryset.filter(organic_class='')
        if self.value() == 'filled':
            # Исключаем все пустые варианты
            return queryset.exclude(organic_class__isnull=True).exclude(organic_class='')
        return queryset


# === 4. ОСНОВНОЙ КЛАСС АДМИНКИ ===
@admin.register(OrganicNames)
class OrganicNamesAdmin(admin.ModelAdmin):
    form = OrganicNamesAdminForm
    search_fields = ['name1', 'name2', 'name3']
    list_display = ('pk', 'name1', 'molecule_short', 'organic_class')
    
    # ИСПРАВЛЕНИЕ: Подключаем оба фильтра в боковую панель админки
    list_filter = (OrganicClassChoicesFilter, OrganicClassEmptyFilter)

    def save_model(self, request, obj, form, change):
        # Сначала вызываем стандартное сохранение
        super().save_model(request, obj, form, change)
        
        # Формируем и выводим ваше кастомное сообщение
        if change:
            msg = f"Редактирована запись № {obj.pk}"
        else:
            msg = f"Создана запись № {obj.pk}"
        messages.success(request, msg)

        
# === СТРУКТУРЫ ДЛЯ БЕСКОНЕЧНОГО ДОБАВЛЕНИЯ КОНТЕНТА К ЗАКОНАМ НЕОРГАНИЧЕСКОЙ ХИМИИ ===

class InorganiclawImageInline(admin.TabularInline):
    model = InorganiclawImage
    extra = 1

class InorganiclawVideoInline(admin.TabularInline):
    model = InorganiclawVideo
    extra = 1

class InorganiclawPresentationInline(admin.TabularInline):
    model = InorganiclawPresentation
    extra = 1


# === ОБНОВЛЕННЫЕ ИСХОДНЫЕ КЛАССЫ ЗАКОНОВ НЕОРГАНИЧЕСКОЙ ХИМИИ ===

# Класс для загрузки/выгрузки знх
class InorganiclawResource(resources.ModelResource):
    class Meta:
        model = Inorganiclaw

# Класс добавления стилей к окну знх
class InorganiclawAdminForm(forms.ModelForm):
    title = forms.CharField(label="Заголовок", widget=CKEditorUploadingWidget())
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())
    formula = forms.CharField(label="Общая формула закона", widget=CKEditorUploadingWidget())
    examples = forms.CharField(label="Примеры", widget=CKEditorUploadingWidget())
    exceptions = forms.CharField(label="Исключения", widget=CKEditorUploadingWidget(), required=False)
    
    class Meta:
        model = Inorganiclaw
        fields = '__all__'

# Класс подробностей знх
class InorganiclawAdmin(ImportExportActionModelAdmin):
    resource_class = InorganiclawResource
    list_display = ('number', 'title', 'display_count', 'pk')
    ordering = ('number',)
    search_fields = ['number', 'title', 'text', 'keywords']
    form = InorganiclawAdminForm
    save_as = True
    
    # Подключаем бесконечные блоки для неорганической химии в самый низ страницы
    inlines = [InorganiclawImageInline, InorganiclawVideoInline, InorganiclawPresentationInline]

    def display_count(self, obj):
        return obj.inorganicreaction_set.count()
        
    display_count.short_description = "реакций"

# Фиксация формы в админке знх
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
    
    # Выводим новые поля в общую таблицу админки
    list_display = ('pk', 'formula', 'name', 'is_interesting',   )
    
    # Позволяет ставить и снимать галочку "интересное" прямо из общего списка, не заходя внутрь вещества
    list_editable = ('is_interesting',)
    
    # Добавляет удобный блок фильтрации в правой колонке админки
    list_filter = ('is_interesting',   )

# фиксация формы в админке вещества
admin.site.register(NamesCompaunds, NamesCompaundsAdmin)


# === СТРУКТУРЫ ДЛЯ БЕСКОНЕЧНОГО ДОБАВЛЕНИЯ КОНТЕНТА К ЗАКОНАМ ОБЩЕЙ ХИМИИ ===

class AtomlawImageInline(admin.TabularInline):
    model = AtomlawImage
    extra = 1

class AtomlawVideoInline(admin.TabularInline):
    model = AtomlawVideo
    extra = 1

class AtomlawPresentationInline(admin.TabularInline):
    model = AtomlawPresentation
    extra = 1


# === ОБНОВЛЕННЫЕ ИСХОДНЫЕ КЛАССЫ ЗАКОНОВ ОБЩЕЙ ХИМИИ ===

# класс для загрузки/выгрузки законы общей химии
class AtomlawResource(resources.ModelResource):
    class Meta:
        model = Atomlaw
        skip_unchanged = True
        report_skipped = True

# класс добавления стилей к окну законы общей химии
class AtomlawAdminForm(forms.ModelForm):
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())
    
    class Meta:
        model = Atomlaw
        fields = '__all__'

# класс подробностей законы общей химии
class AtomlawAdmin(ImportExportActionModelAdmin):
    resource_class = AtomlawResource
    form = AtomlawAdminForm
    search_fields = ['pk', 'title', 'text']
    save_as = True
    list_display = ('pk', 'title')
    
    # Подключаем бесконечные блоки для общей химии в самый низ страницы
    inlines = [AtomlawImageInline, AtomlawVideoInline, AtomlawPresentationInline]

# фиксация формы в админке законы общей химии
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









# === СТРУКТУРЫ ДЛЯ БЕСКОНЕЧНОГО ДОБАВЛЕНИЯ КОНТЕНТА К ЗАКОНАМ ОРГАНИЧЕСКОЙ ХИМИИ ===

class OrganiclawImageInline(admin.TabularInline):
    model = OrganiclawImage
    extra = 1

class OrganiclawVideoInline(admin.TabularInline):
    model = OrganiclawVideo
    extra = 1

class OrganiclawPresentationInline(admin.TabularInline):
    model = OrganiclawPresentation
    extra = 1


# === ОБНОВЛЕННЫЕ ИСХОДНЫЕ КЛАССЫ ЗАКОНОВ ОРГАНИЧЕСКОЙ ХИМИИ ===

# класс для загрузки/выгрузки законы органической химии
class OrganiclawResource(resources.ModelResource):
    class Meta:
        model = Organiclaw

# класс добавления стилей к окну законы органической химии
class OrganiclawAdminForm(forms.ModelForm):
    title = forms.CharField(label="Заголовок", widget=CKEditorUploadingWidget())
    text = forms.CharField(label="Описание закона", widget=CKEditorUploadingWidget())
    exceptions = forms.CharField(label="Исключения", widget=CKEditorUploadingWidget(), required=False)
    
    class Meta:
        model = Organiclaw
        fields = '__all__'

# класс подробностей законы органической химии
class OrganiclawAdmin(ImportExportActionModelAdmin):
    resource_class = OrganiclawResource
    list_display = ('number', 'title' , 'display_count', 'pk')
    ordering = ('number',)
    search_fields = ['number', 'title', 'text', 'keywords']
    form = OrganiclawAdminForm
    save_as = True
    
    # Подключаем бесконечные блоки для органической химии в самый низ страницы
    inlines = [OrganiclawImageInline, OrganiclawVideoInline, OrganiclawPresentationInline]

    def display_count(self, obj):
        return obj.organicreaction_set.count()
        
    display_count.short_description = "реакций"

# фиксация формы в админке законы органической химии
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
