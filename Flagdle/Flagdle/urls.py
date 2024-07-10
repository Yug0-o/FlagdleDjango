"""Flagdle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from game.views import HomeView, ImagesView, FullnameView, GameView, SignUpView, reset_current_score

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('Flagdle/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('Flagdle/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('Flagdle/', HomeView.as_view(), name='home'),
    path('Flagdle/countries/', ImagesView.as_view(), name='countries'),
    path('Flagdle/flags/', FullnameView.as_view(), name='flags'),
    path('Flagdle/game/', GameView.as_view(), name='game'),
    path('Flagdle/reset_current_score/', reset_current_score, name='reset_current_score'),

]
