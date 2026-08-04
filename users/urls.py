from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path
from users import views as UserView
from django.contrib.auth import views as authViews
from . import views

urlpatterns = [
    path('balancechange/', UserView.BalanceChangeView.as_view(), name='balancechange'),
    path('useractivity/<slug:slug>/', views.Useractivityreg, name='useractivity'),
    path('groupchange/<str:str>/', views.RightsEmployeereg, name='groupchange'),
    path('employeereg/', views.Employeereg, name='employeereg'),
    path('heademployeereg/', views.HeadEmployeereg, name='heademployeereg'),
    path('employeeupdate/<str:str>/', views.EmployeeUpdateView, name='employeeupdate'),
    path('employees/', UserView.EmployeesView.as_view(), name='employees'),
    path('companyupdate/', UserView.CompanyUpdateView, name='companyupdate'),
    path('companyprofile/', UserView.CompanyProfileView.as_view(), name='companyprofile'),
    path('profile/', UserView.ProfileView.as_view(), name='profile'),
    
    path('login/', UserView.CustomLoginView.as_view(template_name='users/user.html'), name='user'),
    path('exit/', authViews.LogoutView.as_view(template_name='users/exit.html'), name='exit'),
    
    path('password-reset/', PasswordResetView.as_view(template_name = "users/password_reset_form.html"), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name = "users/password_reset_done.html"), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name='password_reset_complete'),
    
    path('chem/chemprofile/', UserView.ChemProfileView.as_view(), name='chemprofile'),
    path('chem/chemprofilereg/', views.Chemprofilereg, name='chemprofilereg'),
    path('chem/chemuserlogin/', authViews.LoginView.as_view(template_name='users/chemuser.html', next_page='chemprofile'), name='chemuser'),
    path('chem/exit/', authViews.LogoutView.as_view(template_name='users/exit.html', next_page='chemuser'), name='chemexit'),

    # ДОБАВЛЕННЫЙ МАРШРУТ: Личная панель Labjournal
    path('chem/personal/', UserView.PersonalPanelView.as_view(), name='personal_page'),
]
