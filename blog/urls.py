"""
URL configuration for pro1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views


urlpatterns = [ 
    path('', views.index, name="index"), 
    path('first', views.first, name="first"),
    path('search/', views.search_posts, name='search_posts'),
    path('notifications/', views.notifications, name='notifications'), 
    path('login_register',views.login_register,name="login_register"),    
    path('login_view', views.login_view, name="login_view"),
    path('logout_view', views.logout_view, name="logout_view"),
    path('post_detail/<int:pk>/', views.post_detail, name="post_detail"),
    path('post_detail/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post_detail/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('profile', views.profile, name="profile"),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('write', views.write, name="write"),
    path('about', views.about, name="about"),
    path('help', views.help, name="help"),
    path('membership', views.membership, name="membership"),
    path('payment', views.payment, name="payment"),
]

