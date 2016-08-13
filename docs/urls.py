from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^my_subscriptions$', views.home, name='subscriptions_home'),
    url(r'^list_subscriptions$', views.list, name='subscriptions_list'),
    url(r'^add_subscriptions/(?P<sid>[0-9]+)$', views.add, name='subscriptions_add'),
    url(r'^detail_subscriptions/(?P<sid>[a-zA-Z0-9_]+)$', views.detail, name='subscriptions_detail'),
    url(r'^pay_subscriptions/(?P<sid>[0-9]+)/(?P<count>[0-9]+)/$', views.process_payment, name='subscriptions_pay'),
] 