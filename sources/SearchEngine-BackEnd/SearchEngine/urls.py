"""SearchEngine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path
import SearchEngine.views as views

urlpatterns = [
    re_path(r'^search/?$', views.search),
    re_path(r'^detail/?$', views.detail),
    re_path(r'^recommend_words/?$', views.recommend_words),
    re_path(r'^recommend_docs/?$', views.recommend_docs),
    re_path(r'^similar_docs/?$', views.recommend_similar_docs),
    re_path(r'^test/?$', views.test),
]
