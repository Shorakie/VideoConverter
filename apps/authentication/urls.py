from django.urls import path

from .views import (DecoratedTokenObtainPairView, DecoratedTokenRefreshView,
                    RegisterView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', DecoratedTokenObtainPairView.as_view(), name='login'),
    path('refresh_token/', DecoratedTokenRefreshView.as_view(), name='refresh_token'),
]
