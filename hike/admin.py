from django import forms
from django.contrib import admin
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget
import tablib

from ckeditor_uploader.widgets import CKEditorUploadingWidget



# история Карелии классы для отображения в админке

# класс для загрузки/выгрузки Карелия
class KareliahistoryResource(resources.ModelResource):
    class Meta:
        model = Kareliahistory


# класс добавления стилей к окну текст карелия
class KareliahistoryAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Kareliahistory
        fields = '__all__'
        
# класс подробностей Карелия   
class KareliahistoryAdmin(ImportExportActionModelAdmin):
    resource_class = KareliahistoryResource
    list_display = ('pk', 'text',)
    search_fields = ['pk', 'title', 'text']
    form = KareliahistoryAdminForm
        
# фиксация формы в админке Карелия
admin.site.register(Kareliahistory, KareliahistoryAdmin)

# закладки по айти классы для отображения в админке

# класс для загрузки/выгрузки Айти
class ITResource(resources.ModelResource):
    class Meta:
        model = Itbookmarks

# класс добавления стилей к окну текст Айти
class ITAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Itbookmarks
        fields = '__all__'

# класс подробностей Айти   
class ITAdmin(ImportExportActionModelAdmin):
    resource_class = ITResource
    list_display = ('pk', 'type',)
    search_fields = ['pk', 'title', 'text']
    form = ITAdminForm

# фиксация формы в админке Айти
admin.site.register(Itbookmarks, ITAdmin)

# закладки по айти классы для отображения в админке

# 1. Настройка отображения особенностей маршрута в админке
@admin.register(RouteFeature)
class RouteFeatureAdmin(admin.ModelAdmin):
    """Настройка отображения особенностей маршрута в админке"""
    list_display = ('id', 'feature')
    search_fields = ['feature']


# 2. Класс для управления ManyToMany через выпадающие списки с плюсиком
class RouteFeatureInline(admin.TabularInline):
    model = Hike.features.through  # Связующая таблица ManyToMany
    extra = 1                      # Количество пустых выпадающих списков по умолчанию
    verbose_name = "Особенность"
    verbose_name_plural = "Особенности этого маршрута"


# 3. Класс для загрузки/выгрузки хайкинг
class HikeResource(resources.ModelResource):
    class Meta:
        model = Hike


# 4. Класс добавления стилей к окну текст хайкинг
class HikeAdminForm(forms.ModelForm):
    travel_details = forms.CharField(label="Подробности", widget=CKEditorUploadingWidget())
    
    class Meta:
        model = Hike
        fields = '__all__'
        # Исключаем features из стандартного вывода формы, 
        # так как мы выводим его через Inline ниже
        exclude = ('features',)


# 5. Класс подробностей хайкинг   
class HikeAdmin(ImportExportActionModelAdmin):
    resource_class = HikeResource
    # Добавил display_features в список отображения, чтобы видеть особенности в таблице
    list_display = ('pk', 'title', 'display_features')
    search_fields = ['pk', 'title', 'region', 'country']
    form = HikeAdminForm
    
    # Подключаем выпадающие списки особенностей в самый вниз карточки
    inlines = [RouteFeatureInline]

    # Метод для красивого отображения особенностей через запятую в общем списке
    def display_features(self, obj):
        return ", ".join([f.feature for f in obj.features.all()])
    display_features.short_description = 'Особенности'


# 6. Фиксация формы в админке хайкинг
admin.site.register(Hike, HikeAdmin)

# закладки по темам классы для отображения в админке

# класс для загрузки/выгрузки закладки по темам
class BookmarksResource(resources.ModelResource):
    class Meta:
        model = Bookmarks

# класс добавления стилей к окну текст закладки по темам
class BookmarksAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Bookmarks
        fields = '__all__'

# класс подробностей закладки по темам   
class BookmarksAdmin(ImportExportActionModelAdmin):
    resource_class = BookmarksResource
    list_display = ('pk', 'text')
    search_fields = ['pk', 'text']
    form = BookmarksAdminForm

# фиксация формы в админке закладки по темам
admin.site.register(Bookmarks, BookmarksAdmin)


# история семьи классы для отображения в админке

# класс для загрузки/выгрузки история семьи
class FamilyResource(resources.ModelResource):
    class Meta:
        model = Family

# класс добавления стилей к окну текст история семьи
class FamilyAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Family
        fields = '__all__'

# класс подробностей история семьи
class FamilyAdmin(ImportExportActionModelAdmin):
    resource_class = FamilyResource
    list_display = ('pk', 'text')
    search_fields = ['pk', 'text']
    form = FamilyAdminForm

# фиксация формы в админке история семьи
admin.site.register(Family, FamilyAdmin)


# химия классы для отображения в админке

# класс для загрузки/выгрузки химия
class ChemistryResource(resources.ModelResource):
    class Meta:
        model = Chemistry

# класс добавления стилей к окну текст химия
class ChemistryAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    class Meta:
        model = Chemistry
        fields = '__all__'

# класс подробностей химия
class ChemistryAdmin(ImportExportActionModelAdmin):
    resource_class = ChemistryResource
    list_display = ('pk', 'text')
    search_fields = ['pk', 'text']
    form = ChemistryAdminForm

# фиксация формы в админке химия
admin.site.register(Chemistry, ChemistryAdmin)


# история классы для отображения в админке

# класс для загрузки/выгрузки история
class HistoryResource(resources.ModelResource):
    class Meta:
        model = History

# класс добавления стилей к окну текст история
class HistoryAdminForm(forms.ModelForm):
    text = forms.CharField(label="Текст", widget=CKEditorUploadingWidget())
    text_long = forms.CharField(label="Подробности и ссылки", widget=CKEditorUploadingWidget())
    class Meta:
        model = History
        fields = '__all__'

# класс подробностей история
class HistoryAdmin(ImportExportActionModelAdmin):
    resource_class = HistoryResource
    list_display = ('century', 'region', 'year', 'title')
    search_fields = ['pk', 'title', 'text', 'text_long']
    form = HistoryAdminForm

# фиксация формы в админке история
admin.site.register(History, HistoryAdmin)
