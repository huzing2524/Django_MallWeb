# -*- coding: utf-8 -*-
from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r"^usernames/(?P<username>\w{5, 20})/count/$", views.UsernameCountView.as_view()),
    url(r"^mobiles/(?P<mobile>1[3-9]\d{9}/count/$)", views.MobileCountView.as_view()),
    url(r"^users/$", views.UserView.as_view()),
    # 提供了登录签发JWT的视图，默认的返回值仅有token，我们还需在返回值中增加username和user_id
    url(r"^authorizations/$", obtain_jwt_token),
    url(r"^user/$", views.UserDetailView.as_view()),
    url(r"^email/$", views.EmailVIew.as_view()),
    url(r"^emails/verification/$", views.VerifyEmailView.as_view()),
]
