from django.urls import path

from . import views
from . constants import *


urlpatterns = [
    path('', views.HikeAllListView.as_view(), name=URL + 'head'),
    path('bm', views.BMAllListView.as_view(), name='bm'),
    path('it', views.ITAllListView.as_view(), name='it'),
    path('it/searchresult/', views.ITSearchResultView.as_view(), name='itsearchresult'),
    path('<int:pk>/', views.HikeStrView.as_view(), name='hikestr'),
    path('hike/searchresult/', views.SearchResultView.as_view(), name='hikesearchresult'),
    path('filter/<int:pk>', views.filterview, name='bmfilter'),
    path('hikefilter/<int:pk>', views.hikefilterview, name='hikefilteryear'),
    path('donehikefilter/<int:qk>', views.donehikefilterview, name='donehikefilteryear'),
    path('readyhikefilter/<int:rk>', views.readyhikefilterview, name='readyhikefilteryear'),
    path('kareliahistory', views.KareliahistoryAllListView.as_view(), name='kareliahistory'),
    path('kareliahistory/searchresult/', views.KareliahistorySearchResultView.as_view(), name='kareliahistorysearchresult'),
    path('bm/searchresult/', views.BMSearchResultView.as_view(), name='bmsearchresult'),
    path('example', views.ExampleTemplateView.as_view(), name='example'),
    path('family', views.FamilyListView.as_view(), name='family'),
    path('family/searchresult/', views.FamilySearchResultView.as_view(), name='familysearchresult'),
    path('chemistry', views.ChemistryListView.as_view(), name='chemistry'),
    path('chemistry/searchresult/', views.ChemistrySearchResultView.as_view(), name='chemistrysearchresult'),
    path('history', views.HistoryListView.as_view(), name='history'),
    # path('history/searchresult/', views.HistorySearchResultView.as_view(), name='historysearchresult'),
    path('history/<int:pk>/', views.HistoryStrView.as_view(), name='historystr'),
    path('chem/personal/', views.PersonalPanelView.as_view(), name='personal_page'),

    ] 
