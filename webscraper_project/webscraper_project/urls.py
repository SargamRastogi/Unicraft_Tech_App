from django.contrib import admin
from django.urls import path
from webscraper_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('download/', views.download_csv, name='download_csv'),
    path('', views.index, name='home'),
]
