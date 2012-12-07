from piston.handler import BaseHandler
from piston.utils import rc, throttle
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie import fields
from .models import ScraperSession, ScraperProfile


class ScraperProfileResource(ModelResource):
    class Meta:
        queryset = ScraperProfile.objects.all()
        resource_name = 'profile'
        # Authentication
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def get_resource_uri(self, bundle_or_obj):
        return '/api/v1/%s/%s/' % (self._meta.resource_name,bundle_or_obj.obj.id)

    def obj_create(self, bundle, request=None, **kwargs):
        return super(ScraperProfileResource, self).obj_create(bundle, request, user=request.user)

class SessionResource(ModelResource):

    profile = fields.ForeignKey(ScraperProfileResource, 'profile')
    class Meta:
        queryset = ScraperSession.objects.all()
        resource_name = 'session'
        # Authentication
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        profile = ScraperProfile.objects.get(pk=5)
        return super(SessionResource, self).obj_create(bundle, request, profile=profile)
