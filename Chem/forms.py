from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from django import forms
from django.forms import ModelForm


class SearchForm(forms.Form):
    """форма для поиска по полям модели"""
    searchword = forms.CharField(label='Поиск', required=False,
                           help_text='слово для поиска',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('searchword', css_class='form-group col-md-10 mb-0'),
                Row(Submit('submit', 'Найти', css_class='btn  btn-warning col-md-9 mb-3 mt-4 ml-4'))))


class Unswer4Form(forms.Form):
    """форма для внесения ответа с четырьмя окошками"""
    field1 = forms.CharField(label = '', max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    field2 = forms.CharField(label = '', max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    field3 = forms.CharField(label = '', max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    field4 = forms.CharField(label = '', max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
                           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        custom_style = "height: 80px; font-size: 44pt; font-family: Georgia, serif; font-variant-numeric: oldstyle-nums;"
        
        self.helper.layout = Layout(
            Submit('submit', 'Отправить ответ', css_class='mt-3 mb-3 w-100', style="height: 60px;"),
            Row(
                
                Column(Field('field1', style=custom_style), css_class='col-md-3'),
                Column(Field('field2', style=custom_style), css_class='col-md-3'),
                Column(Field('field3', style=custom_style), css_class='col-md-3'),
                Column(Field('field4', style=custom_style), css_class='col-md-3'),
                style="max-width: 1000px; margin: 0 auto;"
            ),
            
            Submit('submit', 'Отправить ответ', css_class='mt-3 w-100', style="height: 60px;")
        )



from crispy_forms.layout import Layout, Field, Submit, Row, Column

class OrganicTestForm(forms.Form):
    """ Форма с 4 длинными полями одно под другим """
    field1 = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Продукт 1'}))
    field2 = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Продукт 2'}))
    field3 = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Продукт 3'}))
    field4 = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Продукт 4'}))
                           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # Чтобы не дублировать <form> в HTML

        # Стиль для длинных полей (высота 60px, текст крупный)
        custom_style = "height: 65px; font-size: 24pt; font-family: Georgia, serif; margin-bottom: 15px;"
        
        self.helper.layout = Layout(
            Row(Column(Field('field1', style=custom_style), css_class='col-12')),
            Row(Column(Field('field2', style=custom_style), css_class='col-12')),
            Row(Column(Field('field3', style=custom_style), css_class='col-12')),
            Row(Column(Field('field4', style=custom_style), css_class='col-12')),
            Submit('submit', 'Отправить ответ', css_class='btn-success btn-lg w-100', style="height: 60px; font-size: 18pt;")
        )
