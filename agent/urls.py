from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('', views.index_page, name='index'),
    path('chat/', views.chat_page, name='chat'),
    path('history/', views.history_page, name='history-page'),
    path('history/clear/', views.clear_history, name='clear-history'),
    path('api/research/',views.ResearchView.as_view(),name='research'),
    path('api/token/', TokenObtainPairView.as_view(),name='token'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('api/research/history/',views.HistoryView.as_view(),name="history"),
    path('api/research/delete/',views.DeleteView.as_view(),name="delete"),
]