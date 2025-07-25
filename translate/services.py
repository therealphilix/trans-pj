from google.cloud import translate_v2 as translate
from google.cloud.exceptions import GoogleCloudError
from django.conf import settings
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class GoogleCloudTranslationService:
    def __init__(self):
        try:
            self.translate_client = translate.Client()
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Translation client: {str(e)}")
            raise

    def translate_text(self, text, target_language, source_language=None):
        """
        Translate text using Google Cloud Translation API
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code
            source_language (str, optional): Source language code
            
        Returns:
            dict: Translation result with translated text, source language, etc.
        """
        try:
            if not text or not text.strip():
                return {'error': 'No text provided for translation'}
            
            # Translate the text
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return {
                'translated_text': result['translatedText'],
                'source_language': result['detectedSourceLanguage'],
                'target_language': target_language,
                'original_text': text,
                'success': True
            }
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Translation API error: {str(e)}")
            return {'error': f'Translation API error: {str(e)}', 'success': False}
        except Exception as e:
            logger.error(f"Unexpected translation error: {str(e)}")
            return {'error': f'Translation failed: {str(e)}', 'success': False}

    def get_supported_languages(self, target_language='en'):
        """
        Get list of supported languages
        
        Args:
            target_language (str): Language code for language names
            
        Returns:
            list: List of supported languages
        """
        try:
            results = self.translate_client.get_languages(target_language=target_language)
            return [
                {
                    'language': lang['language'],
                    'name': lang['name']
                }
                for lang in results
            ]
        except Exception as e:
            logger.error(f"Error fetching supported languages: {str(e)}")
            return []

    def detect_language(self, text):
        """
        Detect the language of given text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Detection result with language code and confidence
        """
        try:
            result = self.translate_client.detect_language(text)
            return {
                'language': result['language'],
                'confidence': result['confidence'],
                'success': True
            }
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return {'error': str(e), 'success': False}

    def translate_batch(self, texts, target_language, source_language=None):
        """
        Translate multiple texts at once
        
        Args:
            texts (list): List of texts to translate
            target_language (str): Target language code
            source_language (str, optional): Source language code
            
        Returns:
            list: List of translation results
        """
        try:
            results = self.translate_client.translate(
                texts,
                target_language=target_language,
                source_language=source_language
            )
            
            return [
                {
                    'translated_text': result['translatedText'],
                    'source_language': result['detectedSourceLanguage'],
                    'target_language': target_language,
                    'original_text': result['input']
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Batch translation error: {str(e)}")
            return [{'error': str(e)} for _ in texts]