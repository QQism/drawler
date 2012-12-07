from django.db import models
from django.contrib.auth.models import User
from forms import UserRegistrationForm
from registration.signals import user_registered

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def user_created(sender, user, request, **kwargs):
        form = UserRegistrationForm(request.POST)
        profile = UserProfile(user=user)
        profile.save()

    user_registered.connect(user_created)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
