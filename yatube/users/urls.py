from django.contrib.auth.views import (
    LogoutView,
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        # Страница выхода из системы
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        # Страница авторизации.
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        # Форма смены пароля.
        PasswordChangeView
        .as_view(template_name='users/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        # Пароль изменен.
        PasswordChangeDoneView
        .as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        # Форма изменения пароля через email.
        PasswordResetView
        .as_view(template_name='users/password_reset_form.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        # Уведомление об отправке ссылки восстановления пароля.
        PasswordResetDoneView
        .as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        # Переход по ссылке из письма.
        PasswordResetConfirmView
        .as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        # Пароль изменен.
        PasswordResetCompleteView
        .as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
