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
    path('compaunds/searchresult/', views.CompaundSearchResultView.as_view(), name='compaundsearchresult'),
    path('compaund/<str:str>/', views.CompaundStrView.as_view(), name='compaund'),

    
    path('atomlaw/test/answer/<str:str>/', views.AtomTestAnswerView.as_view(), name='atomlawtestanswer'),
    path('atomlaws', views.AtomlawView.as_view(), name='atomlaws'),
    path('atomlawstr/<int:pk>/', views.AtomlawStrView.as_view(), name='atomlawstr'),
    path('atomlaw/searchresult/', views.AtomlawSearchResultView.as_view(), name='atomlawsearchresult'),
    path('atomlaw/test/<str:str>/', views.AtomTestHeadView.as_view(), name='atomlawtest'),
    path('atomlaw/test/question/<str:str>/', views.AtomTestQuestionView.as_view(), name='atomlawtestquestion'),
    path('atomlaw/test/answer/<str:str>/', views.AtomTestAnswerView.as_view(), name='atomlawtestanswer'),
    
    path('compaunds', views.CompaundView.as_view(), name='compaunds'),
    

    path('tables', views.TablesView.as_view(), name='tables'),
    path('links', views.LinkView.as_view(), name='links'),

    path('add-reaction/<int:reaction_id>/', views.add_to_list, name='add_reaction'),
    ]
