from django.contrib.auth.hashers import check_password
from django.db.models import Q
from main.models.user_model import User


def authenticate(username, password):
    user = User.objects.filter(Q(email=username) | Q(username=username)).first()
    # print(user)
    if user is None:
        return None
    
    isPasswordCorrect = check_password(password, user.password)
    
    if isPasswordCorrect is False:
        return None
    
    return user