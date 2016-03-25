from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from ivigilate import views_model, views_api, views_integration, views_report

router = routers.DefaultRouter()
router.register(r'accounts', views_model.AccountViewSet)
router.register(r'users', views_model.AuthUserViewSet)
router.register(r'detectors', views_model.DetectorViewSet)
router.register(r'beacons', views_model.BeaconViewSet)
router.register(r'sightings', views_model.SightingViewSet)
router.register(r'events', views_model.EventViewSet)
router.register(r'limits', views_model.LimitViewSet)
router.register(r'notifications', views_model.NotificationViewSet)

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
    url(r'^api/v1/addsightings/$', views_api.AddSightingsView.as_view(), name='addsightings'),
    url(r'^api/v1/autoupdate/$', views_api.AutoUpdateView.as_view(), name='autoupdate'),
    url(r'^api/v1/makepayment/$', views_api.MakePaymentView.as_view(), name='makepayment'),

    url(r'^api/v1/beaconhistory/$', views_api.BeaconHistoryView.as_view(), name='beaconhistory'),
    url(r'^api/v1/detectorhistory/$', views_api.DetectorHistoryView.as_view(), name='detectorhistory'),

    url(r'^api/v1/bclosesighting/$', views_integration.BcloseSightingView.as_view(), name='bclosesighting'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^report/$', views_report.EventOccurrenceReportView.as_view(), name='report'),

    url(r'^.*$', views_api.IndexView.as_view(), name='index'),
)

