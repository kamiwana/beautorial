from django.db.models import Q
from .models import *

class user_idOrEmailBackend(object):
    def authenticate(self, user_id=None, password=None, **kwargs):
        try:
           # Try to fetch the user by searching the user_id or email field
            user = User.objects.get(Q(user_id=user_id)|Q(email=user_id))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)