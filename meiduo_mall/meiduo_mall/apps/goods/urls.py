# -*- coding: utf-8 -*-
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from goods import views

urlpatterns = [
    url(r"^categories/(?P<category_id>\d+)/skus/$", views.SKUListView.as_view())
]

router = DefaultRouter()