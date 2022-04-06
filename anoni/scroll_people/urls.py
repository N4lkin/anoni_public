from django.urls import path
from .views import *

urlpatterns = [
    path('scroll/', GetRandomUserScroll.as_view(), name='get_random_user'),

]
