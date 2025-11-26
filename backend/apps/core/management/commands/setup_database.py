"""
Management command to setup database (run migrations)
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Setup database by running migrations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database setup...'))
        
        try:
            # Run migrations
            self.stdout.write('Running migrations...')
            call_command('migrate', '--noinput', verbosity=2)
            
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise
