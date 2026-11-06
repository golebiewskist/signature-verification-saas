from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, re_path
from django.views.generic import TemplateView

from SignatureApp import settings
from tenant_app import views

urlpatterns = [
    path('sign/', views.SignView.as_view(), name='sign' ),
    path('verify/', views.VerifySignaturesView.as_view(), name='verify' ),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]