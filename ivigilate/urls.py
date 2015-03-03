from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from ivigilate import views

router = routers.DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'users', views.AuthUserViewSet)
router.register(r'places', views.PlaceViewSet)

urlpatterns = patterns('',
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/login/$', views.LoginView.as_view(), name='login'),
    url(r'^api/v1/logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^.*$', views.IndexView.as_view(), name='index'),
)
