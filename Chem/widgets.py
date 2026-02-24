from django import forms

# class JSMEWidget(forms.Widget):
#     # Указываем путь относительно папки templates
#     template_name = 'Chem/widget.html' 

class JSMEWidget(forms.Widget):
    template_name = 'admin/widgets/jsme_editor.html' # создадим этот файл

    def render(self, name, value, attrs=None, renderer=None):
        context = {
            'name': name,
            'value': value if value else "",
            'id': attrs.get('id', 'id_molecule'),
        }
        # Возвращаем HTML-код редактора и поля
        from django.template.loader import render_to_string
        return render_to_string(self.template_name, context)
