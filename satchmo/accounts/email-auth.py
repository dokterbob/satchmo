"""
Allow Satchmo to use an email address instead of the user id as the
primary id
Taken from a posting on the Django mailing list.
Thanks to Vasily Sulatskov for sending this to the list.
"""

from django.contrib.auth.models import User
from django.core.validators import email_re

class BasicBackend:
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class EmailBackend(BasicBackend):
    def authenticate(self, username=None, password=None):
        #If username is an email address, then try to pull it up
        if email_re.search(username):
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            #We have a non-email address username we should try to get
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user