from django import forms
from django.contrib import admin
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget
import tablib

from ckeditor_uploader.widgets import CKEditorUploadingWidget

# Блог классы для отображения в админке

# класс для загрузки/выгрузки Блог
class BlogResource(resources.ModelResource):
    class Meta:
        model = Chem


# класс добавления стилей к окну Блог
class ChemAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Chem
        fields = '__all__'
        
# класс подробностей Блог   
class ChemAdmin(ImportExportActionModelAdmin):
    resource_class = ChemResource
    list_display = ('pk', 'date', 'title',)
    search_fields = ['pk', 'title', 'text']
    form = ChemAdminForm
        
# фиксация формы в админке Блог
admin.site.register(Chem, ChemAdmin)
