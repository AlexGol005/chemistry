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
from .widgets import JSMEWidget




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





# реакции классы для отображения в админке

# класс для загрузки/выгрузки реакции
class InorganicReactionResource(resources.ModelResource):
    class Meta:
        model = InorganicReaction
        skip_unchanged = True
        report_skipped = True   


# класс добавления стилей к окну реакции
class InorganicReactionAdminForm(forms.ModelForm):
    extra = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)


    class Meta:
        model = InorganicReaction
        fields = '__all__'
        
# класс подробностей реакции   
class InorganicReactionAdmin(ImportExportActionModelAdmin):
    resource_class = InorganicReactionResource
    form = InorganicReactionAdminForm
    autocomplete_fields = ['number']

    list_display = ('pk', 'metatitle')


    search_fields = ['pk', 'reagent1', 'reagent2', 'metatitle'] 
    save_as = True
    def save_model(self, request, obj, form, change):
        # Проверяем наличие записи в другой модели
        if not NamesCompaunds.objects.filter(formula=obj.reagent1).exists() and obj.reagent1 != None :
            messages.warning(request, f"Внимание: вещества '{obj.reagent1}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.reagent2).exists() and obj.reagent2 != None :
            messages.warning(request, f"Внимание: вещества '{obj.reagent2}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.reagent3).exists() and obj.reagent3 != None :
            messages.warning(request, f"Внимание: вещества '{obj.reagent3}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.product1).exists() and obj.product1 != None :
            messages.warning(request, f"Внимание: вещества '{obj.product1}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.product2).exists() and obj.product2 != None :
            messages.warning(request, f"Внимание: вещества '{obj.product2}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.product3).exists() and obj.product3 != None :
            messages.warning(request, f"Внимание: вещества '{obj.product3}' нет в модели названий.")
        if not NamesCompaunds.objects.filter(formula=obj.product4).exists() and obj.product4 != None :
            messages.warning(request, f"Внимание: вещества '{obj.product4}' нет в модели названий.")
       
        # Сохранение сработает в любом случае
        super().save_model(request, obj, form, change)
        
# фиксация формы в админке реакции
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
    list_display = ('pk', 'formula', 'name')
    
        
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




class OrganicNamesAdminForm(forms.ModelForm):
    class Meta:
        model = OrganicNames
        fields = '__all__'
        widgets = {
            'smiles': JSMEWidget(attrs={'style': 'display:none;'}), # Прячем текстовое поле
        }

@admin.register(OrganicNames)
class OrganicNamesAdmin(admin.ModelAdmin):
    form = OrganicNamesAdminForm
    list_display = ('name')
    search_fields = ('name')

