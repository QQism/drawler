from django import forms

class ScrapingForm(forms.Form):
    max_pages = forms.IntegerField()
    pages_increment = forms.IntegerField()
    timeout = forms.IntegerField() # milisecond
