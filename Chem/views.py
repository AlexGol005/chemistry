from django.views.generic import ListView, TemplateView

from Chem.models import Chem


class ChemView(ListView):
    """ Выводит список всех постов """
    model = Chem
    template_name = 'Chem/chem.html'
    context_object_name = 'objects'
    ordering = ['-pk']
    paginate_by = 6


class ChemStrView(TemplateView):
    """ выводит отдельный пост """
    model = Chem
    template_name = 'Chem/chemstr.html'


    def get_object(self, queryset=None):
        return Chem.objects.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(ChemStrView, self).get_context_data(**kwargs)
        obj = Chem.objects.get(pk=self.kwargs.get("pk"))
        context['obj'] = obj
        return context
