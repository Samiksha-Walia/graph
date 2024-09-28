from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('select_columns/', views.select_columns, name='select_columns'),
    path('results/', views.results, name='results'),
    path('select_graph_type/', views.select_graph_type, name='select_graph_type'),
    path('generate_graph/', views.generate_graph, name='generate_graph'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('download_image/<str:filename>/', views.download_image, name='download_image'),
    path('download_file/<str:filename>/', views.download_file, name='download_file'),
    path('about/', views.about, name='about'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
