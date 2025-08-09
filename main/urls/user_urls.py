from django.urls import path

from main.views.user_view import *

urlpatterns = [
    path('create-user', UserView.as_view()),
    path('authenticate', LoginView.as_view()),
    path('google-login', GoogleLoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('refreshed-tokens', RefreshedAccessTokens.as_view()),
    path('reset-password', ResetPassword.as_view()),
    path('update-avatar', UpdateAvatar.as_view()),
    path('user-profile', UserProfile.as_view()),
    path('logged-in-user-avatar', GetLoggedInUserAvatar.as_view()),
    path('user-list', UserList.as_view()),
    path('user-search', UserSearch.as_view()),
    path('password-reset', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view()),
]