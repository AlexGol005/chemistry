from django.urls import path


from . import views


urlpatterns = [
    path('', views.ChemView.as_view(), name='chem'),
    path('<int:pk>/', views.ChemStrView.as_view(), name='Chemstr'),
    ]
