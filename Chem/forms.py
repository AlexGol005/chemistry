from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

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
    product1 = forms.CharField(max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    product2 = forms.CharField(max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    product3 = forms.CharField(max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    product4 = forms.CharField(max_length=10000000, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
                           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('product1', style="width: 100px; height: 100px;"),
                Column('product2', style="width: 100px; height: 100px;"),
                Column('product3', style="width: 100px; height: 100px;"),
                Column('product4', style="width: 100px; height: 100px;"'),
              
                Submit('submit', 'отправить ответ', css_class='btn  btn-prima col-md-6 mb-3 mt-4 ml-2 mr-2')))
