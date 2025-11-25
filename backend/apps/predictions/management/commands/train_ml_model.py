"""
Management command to train the ML prediction model
"""
from django.core.management.base import BaseCommand
from apps.predictions.ml_service import MLPredictionService


class Command(BaseCommand):
    help = 'Train the ML model for failure prediction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save the trained model to disk',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting ML model training...')
        
        # Initialize service
        ml_service = MLPredictionService()
        
        # Train model
        self.stdout.write('Training model with historical data...')
        metrics = ml_service.train_model()
        
        # Display metrics
        self.stdout.write(self.style.SUCCESS('\nTraining completed!'))
        self.stdout.write('\nModel Metrics:')
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                self.stdout.write(f'  {metric}: {value:.4f}')
            else:
                self.stdout.write(f'  {metric}: {value}')
        
        # Save model if requested
        if options['save']:
            self.stdout.write('\nSaving model to disk...')
            filepath = ml_service.save_model()
            self.stdout.write(self.style.SUCCESS(f'Model saved to: {filepath}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ ML model training completed successfully!'))
