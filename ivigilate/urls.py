from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from ivigilate import views_model, views_api, views_report

router = routers.DefaultRouter()
router.register(r'accounts', views_model.AccountViewSet)
router.register(r'users', views_model.AuthUserViewSet)
router.register(r'places', views_model.PlaceViewSet)
router.register(r'movables', views_model.MovableViewSet)
router.register(r'sightings', views_model.SightingViewSet)
router.register(r'events', views_model.EventViewSet)

urlpatterns = patterns('',
    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/user/password/done/'}),
    (r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/login/$', views_api.LoginView.as_view(), name='login'),
    url(r'^api/v1/logout/$', views_api.LogoutView.as_view(), name='logout'),
    url(r'^api/v1/addsighting/$', views_api.AddSightingView.as_view(), name='addsighting'),
    url(r'^api/v1/autoupdate/$', views_api.AutoUpdateView.as_view(), name='autoupdate'),
    url(r'^api/v1/makepayment/$', views_api.MakePaymentView.as_view(), name='makepayment'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^report/', views_report.print_users, name='report'),

    url(r'^.*$', views_api.IndexView.as_view(), name='index'),
)
