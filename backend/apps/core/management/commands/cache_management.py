"""
Django management command for cache operations
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.core.cache_utils import cache_manager, invalidate_cache_pattern


class Command(BaseCommand):
    help = 'Manage cache operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['clear', 'stats', 'invalidate'],
            help='Action to perform'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Pattern to invalidate (for invalidate action)'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'clear':
            self.clear_cache()
        elif action == 'stats':
            self.show_stats()
        elif action == 'invalidate':
            pattern = options.get('pattern')
            if not pattern:
                self.stdout.write(self.style.ERROR('Pattern is required for invalidate action'))
                return
            self.invalidate_pattern(pattern)

    def clear_cache(self):
        """Clear all cache"""
        self.stdout.write('Clearing all cache...')
        cache.clear()
        self.stdout.write(self.style.SUCCESS('✓ Cache cleared successfully'))

    def show_stats(self):
        """Show cache statistics"""
        self.stdout.write('Cache Statistics:')
        self.stdout.write('-' * 50)
        
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Obtener info de Redis
            info = redis_conn.info()
            
            self.stdout.write(f"Redis Version: {info.get('redis_version', 'N/A')}")
            self.stdout.write(f"Used Memory: {info.get('used_memory_human', 'N/A')}")
            self.stdout.write(f"Connected Clients: {info.get('connected_clients', 'N/A')}")
            self.stdout.write(f"Total Keys: {redis_conn.dbsize()}")
            
            # Obtener algunas keys de ejemplo
            keys = redis_conn.keys('cmms:*')[:10]
            if keys:
                self.stdout.write('\nSample Keys:')
                for key in keys:
                    self.stdout.write(f"  - {key.decode()}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting stats: {e}'))

    def invalidate_pattern(self, pattern):
        """Invalidate cache by pattern"""
        self.stdout.write(f'Invalidating cache pattern: {pattern}')
        invalidate_cache_pattern(pattern)
        self.stdout.write(self.style.SUCCESS(f'✓ Pattern "{pattern}" invalidated'))
