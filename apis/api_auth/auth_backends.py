from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class MultiDBAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        db = getattr(request, 'db', 'default') 
       
        UserModel = get_user_model()

        try:
            user = UserModel.objects.using(db).get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None