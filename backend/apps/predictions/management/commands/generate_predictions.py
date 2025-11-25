"""
Management command to generate predictions for all assets
"""
from django.core.management.base import BaseCommand
from apps.assets.models import Asset
from apps.predictions.ml_service import MLPredictionService


class Command(BaseCommand):
    help = 'Generate failure predictions for all operational assets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--asset-id',
            type=str,
            help='Generate prediction for a specific asset ID',
        )

    def handle(self, *args, **options):
        self.stdout.write('Generating failure predictions...')
        
        # Initialize ML service
        ml_service = MLPredictionService()
        
        # Load or train model
        if not ml_service.load_model():
            self.stdout.write('No saved model found. Training new model...')
            ml_service.train_model()
        
        # Get assets
        if options['asset_id']:
            assets = Asset.objects.filter(id=options['asset_id'])
            if not assets.exists():
                self.stdout.write(self.style.ERROR(f'Asset with ID {options["asset_id"]} not found'))
                return
        else:
            assets = Asset.objects.filter(status__in=['OPERATIONAL', 'MAINTENANCE'])
        
        self.stdout.write(f'Processing {assets.count()} assets...\n')
        
        # Generate predictions
        predictions_created = 0
        alerts_created = 0
        
        for asset in assets:
            try:
                prediction = ml_service.create_prediction_for_asset(asset)
                predictions_created += 1
                
                # Count alerts
                if prediction.failure_probability >= 50:
                    alerts_created += 1
                
                # Display result
                risk_color = self.style.ERROR if prediction.risk_level == 'CRITICAL' else \
                            self.style.WARNING if prediction.risk_level == 'HIGH' else \
                            self.style.SUCCESS
                
                self.stdout.write(
                    f'  {asset.name}: {prediction.failure_probability}% '
                    f'({risk_color(prediction.get_risk_level_display())})'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error processing {asset.name}: {str(e)}')
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Generated {predictions_created} predictions'))
        if alerts_created > 0:
            self.stdout.write(self.style.WARNING(f'⚠ Created {alerts_created} alerts for high-risk assets'))
