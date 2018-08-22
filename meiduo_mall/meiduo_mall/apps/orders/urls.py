# -*- coding: utf-8 -*-
from django.conf.urls import url

from orders import views

urlpatterns = [
    url(r"^orders/settlement/$", views.OrderSettlementView.as_view()),
    url(r"^orders/$", views.SaveOrderView.as_view())
]
