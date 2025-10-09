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
class InorganiclawResource(resources.ModelResource):
    class Meta:
        model = Inorganiclaw


# класс добавления стилей к окну Блог
class InorganiclawAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Inorganiclaw
        fields = '__all__'
        
# класс подробностей Блог   
class InorganiclawAdmin(ImportExportActionModelAdmin):
    resource_class = InorganiclawResource
    list_display = ('pk', 'date', 'title',)
    search_fields = ['pk', 'title', 'text']
    form = InorganiclawAdminForm
        
# фиксация формы в админке Блог
admin.site.register(Inorganiclaw, InorganiclawAdmin)
