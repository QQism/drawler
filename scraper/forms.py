from django import forms

def add_control_label(f):
    def control_label_tag(self, contents=None, attrs=None):
        if attrs is None: attrs = {}
        attrs['class'] = 'control-label'
        return f(self, contents, attrs)
    return control_label_tag

forms.forms.BoundField.label_tag = add_control_label(forms.forms.BoundField.label_tag)

class ScraperSessionForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    max_pages = forms.IntegerField()
#    pages_increment = forms.IntegerField()
    callback_url = forms.URLField(required=False)
    timeout = forms.IntegerField(required=False) # milisecond

class ScraperProfileForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    

    name = forms.CharField(help_text='Profile name')
    url = forms.URLField(help_text="""
                         By default, drawler will <strong>automatically</strong> discover new URLs based on this URL. However, you can force crawling with a URL pattern<br/>
                         Ex: crawling http://abc.com/1.html,..., http://abc.com/99.html
                         <b>http://abc.com/{{1-99}}.html</b>
                         """)
    template = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Fill the template'}))
    keywords = forms.CharField(required=False,
            widget=forms.Textarea(attrs={'placeholder': 'Keywords separate by commas'}))
