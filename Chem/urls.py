from django.urls import path


from . import views


urlpatterns = [
    # path('organicnamestesthead', views.OrganicNamesHomeView.as_view(), name='organicnamestesthead'),
    # path('organicnamestest/<int:pk>/', views.OrganicNamesTestView.as_view(), name='organicnamestest'),
    
    path('', views.ChemView.as_view(), name='chem'),
    path('inorganiclaw', views.InorganiclawView.as_view(), name='inorganiclaw'),
    path('<int:pk>/', views.InorganiclawStrView.as_view(), name='inorganiclawstr'),
    path('inorganiclaw/searchresult/', views.ChemSearchResultView.as_view(), name='inorganiclawsearchresult'),
    path('inorganiclaw/test/<str:str>/', views.ChemTestHeadView.as_view(), name='inorganiclawtest'),
    path('inorganiclaw/test/question/<str:str>/', views.ChemTestQuestionView.as_view(), name='inorganiclawtestquestion'),
    path('inorganiclaw/test/answer/<str:str>/', views.ChemTestAnswerView.as_view(), name='inorganiclawtestanswer'),


    path('organiclaw', views.OrganiclawView.as_view(), name='organiclaw'),
    path('organiclawstr/<int:pk>/', views.OrganiclawStrView.as_view(), name='organiclawstr'),
    path('organiclaw/searchresult/', views.OrganicChemSearchResultView.as_view(), name='organiclawsearchresult'),
    path('organiclaw/test/<str:str>/', views.OrganicChemTestHeadView.as_view(), name='organiclawtest'),
    path('organiclaw/test/question/<str:str>/', views.OrganicChemTestQuestionView.as_view(), name='organiclawtestquestion'),
    path('organiclaw/test/answer/<str:str>/', views.OrganicChemTestAnswerView.as_view(), name='organiclawtestanswer'),
    
    path('atomlaw/test/answer/<str:str>/', views.AtomTestAnswerView.as_view(), name='atomlawtestanswer'),
    path('atomlaws', views.AtomlawView.as_view(), name='atomlaws'),
    path('atomlawstr/<int:pk>/', views.AtomlawStrView.as_view(), name='atomlawstr'),
    path('atomlaw/searchresult/', views.AtomlawSearchResultView.as_view(), name='atomlawsearchresult'),
    path('atomlaw/test/<str:str>/', views.AtomTestHeadView.as_view(), name='atomlawtest'),
    path('atomlaw/test/question/<str:str>/', views.AtomTestQuestionView.as_view(), name='atomlawtestquestion'),
    path('atomlaw/test/answer/<str:str>/', views.AtomTestAnswerView.as_view(), name='atomlawtestanswer'),
    
    path('compaunds', views.CompaundView.as_view(), name='compaunds'),
    path('compaunds/searchresult/', views.CompaundSearchResultView.as_view(), name='compaundsearchresult'),
    path('compaund/<str:str>/', views.CompaundStrView.as_view(), name='compaund'),

    path('organiccompaunds', views.OrganicCompaundView.as_view(), name='organiccompaunds'),
    path('organiccompaunds/searchresult/', views.OrganicCompaundSearchResultView.as_view(), name='organiccompaundsearchresult'),
    path('organiccompaund/<str:str>/', views.OrganicCompaundStrView.as_view(), name='organiccompaund'),

    path('organicnamestest/', views.organicnamestest_start, name='organicnamestest_start'),
    path('organicnamestest/question/<int:index>/', views.organicnamestest_question, name='organicnamestest_question'),
    path('organicnamestest/answer/<int:index>/', views.organicnamestest_answer, name='organicnamestest_answer'),
    

    path('tables', views.TablesView.as_view(), name='tables'),
    path('links', views.LinkView.as_view(), name='links'),

    path('add-reaction/<int:reaction_id>/', views.add_to_list, name='add_reaction'),
    path('chem/remove-reaction/<int:reaction_id>/', views.remove_reaction, name='remove_reaction'),
    path('chem/my-list/', views.my_reactions_list, name='my_reactions_list'),
    path('my-reactions-test/', views.ChemMyTestHeadView.as_view(), name='my_reactions_test'),


    path('organic_add-reaction/<int:reaction_id>/', views.organic_add_to_list, name='organic_add_reaction'),
    path('chem/organic_remove_reaction-reaction/<int:reaction_id>/', views.organic_remove_reaction, name='organic_remove_reaction'),
    path('chem/oganic_my-list/', views.organic_my_reactions_list, name='organic_my_reactions_list'),
    path('organic_my-reactions-test/', views.OrganicChemMyTestHeadView.as_view(), name='organic_my_reactions_test'),
    ]
