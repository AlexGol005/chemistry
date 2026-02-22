from django import forms

class JSMEWidget(forms.Widget):
    # Указываем путь относительно папки templates
    template_name = 'Chem/widget.html' 
