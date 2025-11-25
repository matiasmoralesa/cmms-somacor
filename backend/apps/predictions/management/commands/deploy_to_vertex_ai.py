"""
Management command to deploy ML model to Vertex AI
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.predictions.vertex_ai_client import get_vertex_ai_client


class Command(BaseCommand):
    help = 'Deploy the trained ML model to Google Cloud Vertex AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-path',
            type=str,
            default='ml_models/failure_prediction_model.joblib',
            help='Path to the trained model file',
        )
        parser.add_argument(
            '--model-name',
            type=str,
            default='cmms-failure-prediction',
            help='Display name for the model in Vertex AI',
        )

    def handle(self, *args, **options):
        self.stdout.write('Deploying model to Vertex AI...')
        
        # Check if Vertex AI is enabled
        if not settings.USE_VERTEX_AI:
            self.stdout.write(
                self.style.WARNING(
                    '\nVertex AI is not enabled in settings.'
                    '\nSet USE_VERTEX_AI=True and configure GCP_PROJECT_ID to enable.'
                    '\n\nFor development, the system will use the local model.'
                )
            )
            return
        
        # Check GCP configuration
        if not settings.GCP_PROJECT_ID:
            self.stdout.write(
                self.style.ERROR(
                    'GCP_PROJECT_ID is not configured. '
                    'Set it in your environment variables.'
                )
            )
            return
        
        # Get Vertex AI client
        client = get_vertex_ai_client()
        
        if not client.client_initialized:
            self.stdout.write(
                self.style.ERROR(
                    'Failed to initialize Vertex AI client. '
                    'Make sure google-cloud-aiplatform is installed.'
                )
            )
            return
        
        # Deploy model
        self.stdout.write(f'\nDeploying model from: {options["model_path"]}')
        self.stdout.write(f'Model name: {options["model_name"]}')
        self.stdout.write(f'Project: {settings.GCP_PROJECT_ID}')
        self.stdout.write(f'Location: {settings.GCP_LOCATION}\n')
        
        endpoint_id = client.deploy_model(
            model_path=options['model_path'],
            model_display_name=options['model_name']
        )
        
        if endpoint_id:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Model deployed successfully!'
                    f'\nEndpoint ID: {endpoint_id}'
                    f'\n\nUpdate your .env file with:'
                    f'\nVERTEX_AI_ENDPOINT_ID={endpoint_id}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('\n✗ Failed to deploy model to Vertex AI')
            )
