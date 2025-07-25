from google.cloud import translate_v2 as translate
from google.cloud.exceptions import GoogleCloudError
from django.conf import settings
from google.oauth2 import service_account
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Create credentials from environment variables
def get_google_credentials():
    credentials_dict = {
        "type": "service_account",
        "project_id": os.getenv('PROJECT_ID'),
        "private_key_id": os.getenv('PRIVATE_KEY_ID'),
        "private_key": os.getenv('PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.getenv('CLIENT_EMAIL'),
        "client_id": os.getenv('CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('CLIENT_EMAIL')}",
        "universe_domain": "googleapis.com"
    }
    
    return service_account.Credentials.from_service_account_info(credentials_dict)

class GoogleCloudTranslationService:
    def __init__(self):
        try:
            # Get credentials and pass them to the client
            credentials = get_google_credentials()
            self.translate_client = translate.Client(credentials=credentials)
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