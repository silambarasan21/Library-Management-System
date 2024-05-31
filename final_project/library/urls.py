"""
URL configuration for one project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from library import views as app_view
from django.conf.urls.static import static
from final_project import settings
urlpatterns = [
    path('',app_view.home,name = 'home'),
    path('usersignup',app_view.usersignup,name='signup'),
    path('adminsignup',app_view.adminsignup,name='adminsignup'),
    path('add_book',app_view.lib,name='book'),
    path('userlogin',app_view.userlogin,name='userlogin'),
    path('adminlogin',app_view.adminlogin,name='adminlogin'),
    path('bookdetails',app_view.bookdetails,name='Bookdetails'),
    
    path('updatebook/<pk>',app_view.updatebook,name='updatebook'),
    path('deletebook/<pk>',app_view.deletebook,name='deletebook'),
    path('take',app_view.take,name='take'),
    path('takebook/<pk>',app_view.takebook,name='takebook'),
    path('retainbook/<pk>',app_view.retainbook,name='retainbook'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)