# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter

from areas import views

urlpatterns = []

router = DefaultRouter()
router.register("areas", views.AreasViewSet, base_name="areas")

urlpatterns += router.urls
