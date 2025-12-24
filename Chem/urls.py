from django.urls import path


from . import views


urlpatterns = [
    path('', views.ChemView.as_view(), name='chem'),
    path('inorganiclaw', views.InorganiclawView.as_view(), name='inorganiclaw'),
    path('<int:pk>/', views.InorganiclawStrView.as_view(), name='inorganiclawstr'),
    path('inorganiclaw/searchresult/', views.ChemSearchResultView.as_view(), name='inorganiclawsearchresult'),
    path('inorganiclaw/test/<str:str>/', views.ChemTestHeadView.as_view(), name='inorganiclawtest'),
    path('inorganiclaw/test/question/<str:str>/', views.ChemTestQuestionView.as_view(), name='inorganiclawtestquestion'),
    path('inorganiclaw/test/answer/<str:str>/', views.ChemTestAnswerView.as_view(), name='inorganiclawtestanswer'),
    ]
