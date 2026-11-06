from django.urls import path

from . import views
from . constants import *


from django.urls import path
from . import views

urlpatterns = [
    # Главная страница списка походов (теперь с поддержкой всех GET-фильтров)
    path('', views.HikeAllListView.as_view(), name='hikehead'),
    path('<int:pk>/', views.HikeStrView.as_view(), name='hikestr'),

    # Старые пути фильтров и поиска походов (перенаправляем на ту же универсальную вьюшку HikeAllListView)
    path('hike/searchresult/', views.HikeAllListView.as_view(), name='hikesearchresult'),
    path('hikefilter/<int:pk>', views.HikeAllListView.as_view(), name='hikefilteryear'),
    path('donehikefilter/<int:qk>', views.HikeAllListView.as_view(), name='donehikefilteryear'),
    path('readyhikefilter/<int:rk>', views.HikeAllListView.as_view(), name='readyhikefilteryear'),

    # Маршруты для разделов БМ 
    path('bm', views.BMAllListView.as_view(), name='bm'),
    path('bm/searchresult/', views.BMSearchResultView.as_view(), name='bmsearchresult'),
    path('filter/<int:pk>', views.filterview, name='bmfilter'),

    # Маршруты для разделов IT
    path('it', views.ITAllListView.as_view(), name='it'),
    path('it/searchresult/', views.ITSearchResultView.as_view(), name='itsearchresult'),

    # История Карелии
    path('kareliahistory', views.KareliahistoryAllListView.as_view(), name='kareliahistory'),
    path('kareliahistory/searchresult/', views.KareliahistorySearchResultView.as_view(), name='kareliahistorysearchresult'),

    # Семья и Химия
    path('family', views.FamilyListView.as_view(), name='family'),
    path('family/searchresult/', views.FamilySearchResultView.as_view(), name='familysearchresult'),
    path('chemistry', views.ChemistryListView.as_view(), name='chemistry'),
    path('chemistry/searchresult/', views.ChemistrySearchResultView.as_view(), name='chemistrysearchresult'),

    # Общая история
    path('history', views.HistoryListView.as_view(), name='history'),
    path('history/<int:pk>/', views.HistoryStrView.as_view(), name='historystr'),

    # Панель и примеры
    path('example', views.ExampleTemplateView.as_view(), name='example'),
    path('chem/personal/', views.PersonalPanelView.as_view(), name='personal_page'),
]

