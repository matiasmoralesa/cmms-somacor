"""
Management command to load sample assets for testing
"""
from django.core.management.base import BaseCommand
from apps.assets.models import Asset, Location
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Load sample assets for testing'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample assets...')
        
        # Create default location
        location, created = Location.objects.get_or_create(
            name='Base Principal',
            defaults={
                'address': 'Av. Principal 123, Santiago',
                'description': 'Ubicación principal de la flota',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created location: {location.name}'))
        else:
            self.stdout.write(f'  Location already exists: {location.name}')
        
        # Get admin user as created_by
        admin_user = User.objects.filter(role__name='ADMIN').first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('✗ No admin user found. Run init_data first.'))
            return
        
        # Sample assets data
        sample_assets = [
            {
                'name': 'Camión Supersucker 001',
                'asset_code': 'CS-001',
                'vehicle_type': Asset.CAMION_SUPERSUCKER,
                'serial_number': 'SS2024001',
                'license_plate': 'ABCD-12',
                'manufacturer': 'Volvo',
                'model': 'FM 440',
                'status': Asset.STATUS_OPERATIONAL,
                'specifications': {'year': 2022, 'engine': 'D13K440'},
            },
            {
                'name': 'Camioneta MDO 001',
                'asset_code': 'CM-001',
                'vehicle_type': Asset.CAMIONETA_MDO,
                'serial_number': 'CM2024001',
                'license_plate': 'EFGH-34',
                'manufacturer': 'Toyota',
                'model': 'Hilux',
                'status': Asset.STATUS_OPERATIONAL,
                'specifications': {'year': 2023, 'engine': '2.8L Diesel'},
            },
            {
                'name': 'Retroexcavadora MDO 001',
                'asset_code': 'RE-001',
                'vehicle_type': Asset.RETROEXCAVADORA_MDO,
                'serial_number': 'RE2024001',
                'license_plate': None,
                'manufacturer': 'Caterpillar',
                'model': '420F',
                'status': Asset.STATUS_OPERATIONAL,
                'specifications': {'year': 2021, 'engine': 'Cat C4.4'},
            },
            {
                'name': 'Cargador Frontal MDO 001',
                'asset_code': 'CF-001',
                'vehicle_type': Asset.CARGADOR_FRONTAL_MDO,
                'serial_number': 'CF2024001',
                'license_plate': None,
                'manufacturer': 'Caterpillar',
                'model': '950M',
                'status': Asset.STATUS_OPERATIONAL,
                'specifications': {'year': 2022, 'engine': 'Cat C7.1'},
            },
            {
                'name': 'Minicargador MDO 001',
                'asset_code': 'MC-001',
                'vehicle_type': Asset.MINICARGADOR_MDO,
                'serial_number': 'MC2024001',
                'license_plate': None,
                'manufacturer': 'Bobcat',
                'model': 'S650',
                'status': Asset.STATUS_OPERATIONAL,
                'specifications': {'year': 2023, 'engine': 'Kubota V2607'},
            },
        ]
        
        assets_created = 0
        assets_updated = 0
        
        for asset_data in sample_assets:
            asset_code = asset_data['asset_code']
            
            asset, created = Asset.objects.update_or_create(
                asset_code=asset_code,
                defaults={
                    **asset_data,
                    'location': location,
                    'created_by': admin_user,
                }
            )
            
            if created:
                assets_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created asset: {asset_code} - {asset.name}')
                )
            else:
                assets_updated += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated asset: {asset_code} - {asset.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Loaded {assets_created} new assets, '
                f'updated {assets_updated} existing assets'
            )
        )
