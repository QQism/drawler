from django import forms
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _

attrs_dict = {'class': 'required'}

class UserRegistrationForm(RegistrationForm):
    pass
