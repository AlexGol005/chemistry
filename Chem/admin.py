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
    list_display = ('number', 'title', 'pk')
    ordering = ('number',)
    search_fields = ['number', 'title', 'text', 'keywords']
    form = InorganiclawAdminForm
    save_as = True
        
# фиксация формы в админке знх
admin.site.register(Inorganiclaw, InorganiclawAdmin)


# тесты по неорганике
# admin.site.register(InorganicReaction) 

@admin.register(InorganicReaction)
class InorganicReactionAdmin(admin.ModelAdmin):    
    search_fields = ['pk', 'reagent1', 'reagent2'] 
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

# названия веществ


# @admin.register(NamesCompaunds)
# class NamesCompaundsAdmin(admin.ModelAdmin):
    
#     search_fields = ['pk', 'formula', 'name'] 
#     save_as = True
#     list_display = ('pk', 'formula', 'name')
    


# вещества классы для отображения в админке

# класс для загрузки/выгрузки вещества
class NamesCompaundsResource(resources.ModelResource):
    class Meta:
        model = NamesCompaunds


# класс добавления стилей к окну вещества
class NamesCompaundsAdminForm(forms.ModelForm):
    apperance = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget(), required=False)


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
