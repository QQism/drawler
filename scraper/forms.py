from django import forms

class ScraperSessionForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    max_pages = forms.IntegerField()
    pages_increment = forms.IntegerField()
    callback_url = forms.URLField(required=False)
    timeout = forms.IntegerField(required=False) # milisecond

class ScraperProfileForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    name = forms.CharField()
    url = forms.URLField()
    template = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Fill the template'}))
    keywords = forms.CharField(required=False,
            widget=forms.Textarea(attrs={'placeholder': 'Keywords separate by commas'}))
