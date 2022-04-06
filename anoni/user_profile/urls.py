from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('register/<slug:uuid_link>/', ConfirmRegistrations.as_view(), name='confirm_register'),
    path('settings/', UserSettingsProfile.as_view(), name='settings_profile_data'),
    path('filter_settings/', UserFilterSettingsProfile.as_view(), name='filter_settings_data'),
    path('reset/', UserRestorePassword.as_view(), name='user_restore_password'),
    path('reset/<slug:uuid_link>/', UserRestorePasswordConfirm.as_view(), name='user_restore_password_confirm'),
]
