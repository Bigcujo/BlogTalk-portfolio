from django.forms import ModelForm
from django import forms
from .models import GroupMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class chatmessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body' : forms.TextInput(attrs={'placeholder': 'Add message ...', 
                                             'maxlength': '300', 
                                             'autofocus': True})
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Send'))