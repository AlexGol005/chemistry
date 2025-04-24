from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from .forms import AttestationJForm
from .models import AttestationJ, ResultValueJ


class Contacts(View):
    """выводит страницу контакты"""
    def get(self, request):
        return render(request, 'main/contacts.html')


class IndexView(View):
    """выводит страницу главная страница по основному адресу"""
    def get(self, request):
        return render(request, 'main/main.html')


class EquipmentView(LoginRequiredMixin, TemplateView):
    """выводит страницу Инфраструктура лаборатории"""
    template_name = 'main/equipment.html'

    def get_context_data(self, **kwargs):
        context = super(EquipmentView, self).get_context_data(**kwargs)
        try:
            user = User.objects.get(username=self.request.user)
            if user.is_staff:
                context['USER'] = True
            if not user.is_staff:
                context['USER'] = False
        except:
            context['USER'] = False
        return context
