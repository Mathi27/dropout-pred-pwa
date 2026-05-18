from django.urls import path

from apps.core.views import AdminAnalyticsView, DoctorAnalyticsView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("analytics/admin/", AdminAnalyticsView.as_view(), name="analytics-admin"),
    path("analytics/doctor/", DoctorAnalyticsView.as_view(), name="analytics-doctor"),
]
