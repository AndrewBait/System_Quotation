from django.urls import path
from .views import register_view, login_view, logout_view, home_view, home_view, mark_notification_as_read

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('mark_notification_as_read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
]
