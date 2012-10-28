from django.db import models

class ScraperProfile(models.Model):
    name = models.CharField('Name', max_length=255, null=False, blank=False)
    url = models.URLField('URL', max_length=200, null=False, blank=False)
    template = models.TextField('Template', blank=True, default='')
    keywords_text = models.TextField('Keywords', blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def keywords(self):
        return self.keywords_text.split(',')

    def save(self, *args, **kwargs):
        self.keywords_text = ','.join([keyword.strip()
                                       for keyword in
                                       self.keywords_text.split(',')])
        super(type(self), self).save(*args, **kwargs)


    def __unicode__(self):
        return self.name + ': ' + self.url + ', ' + self.keywords_text
