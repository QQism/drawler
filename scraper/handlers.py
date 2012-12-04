from piston.handler import BaseHandler
from piston.utils import rc, throttle

from . import models

class ScraperSessionHandler(BaseHandler):
    model = models.ScraperSession
    allowed_methods = ('GET', 'POST',)

    def read(self, request, pk):
        session = models.ScraperSession.objects.get(pk=pk)
        return session
