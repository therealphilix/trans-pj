from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import GoogleCloudTranslationService
from .models import Translation
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Home page with translation interface—fetch languages from API only."""
    service = GoogleCloudTranslationService()
    try:
        # service.get_supported_languages() should return a list of dicts
        # with keys "language" (the ISO code) and "name" (the human name)
        supported_languages = service.get_supported_languages()
    except Exception as e:
        logger.error(f"Failed to fetch supported languages: {e}")
        # fallback to a minimal set so the UI doesn’t completely break
        supported_languages = [
            {"language": "en", "name": "English"},
            {"language": "es", "name": "Spanish"},
            {"language": "fr", "name": "French"},
        ]

    return render(request, 'translator/home.html', {
        'supported_languages': supported_languages
    })

@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    """Handle translation requests"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang')
        target_lang = data.get('target_lang')
        
        # Validation
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        
        if not target_lang:
            return JsonResponse({'error': 'Target language not specified'}, status=400)
        
        # Initialize translation service
        service = GoogleCloudTranslationService()
        
        # Perform translation
        result = service.translate_text(
            text=text,
            target_language=target_lang,
            source_language=source_lang if source_lang != 'auto' else None
        )
        
        # Handle translation result
        if result.get('success'):
            
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return JsonResponse({'error': 'Translation service unavailable'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def detect_language(request):
    """Detect language of provided text"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        
        service = GoogleCloudTranslationService()
        result = service.detect_language(text)
        
        return JsonResponse(result)
    
    except Exception as e:
        logger.error(f"Language detection error: {str(e)}")
        return JsonResponse({'error': 'Language detection failed'}, status=500)

# def translation_history(request):
#     """View translation history"""
#     if request.user.is_authenticated:
#         translations = Translation.objects.filter(user=request.user)
#     else:
#         translations = Translation.objects.filter(user=None)
    
#     paginator = Paginator(translations, 10)  # Show 10 translations per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'translator/history.html', {
#         'page_obj': page_obj,
#         'translations': page_obj.object_list
#     })

@login_required
def delete_translation(request, translation_id):
    """Delete a translation from history"""
    try:
        translation = Translation.objects.get(
            id=translation_id,
            user=request.user
        )
        translation.delete()
        messages.success(request, 'Translation deleted successfully.')
    except Translation.DoesNotExist:
        messages.error(request, 'Translation not found.')
    
    return redirect('history')

def supported_languages_view(request):
    """View all supported languages"""

    service = GoogleCloudTranslationService()
    try:
        # service.get_supported_languages() should return a list of dicts
        # with keys "language" (the ISO code) and "name" (the human name)
        supported_languages = service.get_supported_languages()
    except Exception as e:
        logger.error(f"Failed to fetch supported languages: {e}")
        # fallback to a minimal set so the UI doesn’t completely break
        supported_languages = [
            {"language": "en", "name": "English"},
            {"language": "es", "name": "Spanish"},
            {"language": "fr", "name": "French"},
        ]


    return render(request, 'translator/languages.html', {
        'languages': supported_languages
    })