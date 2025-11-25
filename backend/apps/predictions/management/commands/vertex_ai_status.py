"""
Management command to check Vertex AI status
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.predictions.vertex_ai_client import get_vertex_ai_client


class Command(BaseCommand):
    help = 'Check Vertex AI configuration and status'

    def handle(self, *args, **options):
        self.stdout.write('Checking Vertex AI configuration...\n')
        
        # Display configuration
        self.stdout.write('Configuration:')
        self.stdout.write(f'  USE_VERTEX_AI: {settings.USE_VERTEX_AI}')
        self.stdout.write(f'  GCP_PROJECT_ID: {settings.GCP_PROJECT_ID or "Not configured"}')
        self.stdout.write(f'  GCP_LOCATION: {settings.GCP_LOCATION}')
        self.stdout.write(f'  VERTEX_AI_ENDPOINT_ID: {settings.VERTEX_AI_ENDPOINT_ID or "Not configured"}')
        
        # Get client
        client = get_vertex_ai_client()
        
        # Get model info
        self.stdout.write('\nModel Status:')
        model_info = client.get_model_info()
        
        for key, value in model_info.items():
            self.stdout.write(f'  {key}: {value}')
        
        # List models if available
        if model_info.get('vertex_ai_enabled'):
            self.stdout.write('\nAvailable Models:')
            models = client.list_models()
            
            if models:
                for model in models:
                    self.stdout.write(f'\n  Model: {model["name"]}')
                    self.stdout.write(f'    Resource: {model["resource_name"]}')
                    self.stdout.write(f'    Created: {model["create_time"]}')
            else:
                self.stdout.write('  No models found')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if model_info['status'] == 'deployed':
            self.stdout.write(self.style.SUCCESS('\n✓ Vertex AI is configured and operational'))
        elif model_info['status'] == 'local':
            self.stdout.write(self.style.WARNING('\n⚠ Using local model (Vertex AI not configured)'))
        else:
            self.stdout.write(self.style.ERROR('\n✗ Vertex AI configuration error'))
