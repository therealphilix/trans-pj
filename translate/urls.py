from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('translate/', views.translate_text, name='translate'),
    path('detect/', views.detect_language, name='detect'),
    # path('history/', views.translation_history, name='history'),
    path('delete/<int:translation_id>/', views.delete_translation, name='delete_translation'),
    path('languages/', views.supported_languages_view, name='languages'),
]