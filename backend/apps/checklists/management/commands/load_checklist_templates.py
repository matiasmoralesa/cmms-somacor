"""
Management command to load checklist templates from JSON file
"""
import json
from django.core.management.base import BaseCommand
from apps.checklists.models import ChecklistTemplate


class Command(BaseCommand):
    help = 'Load checklist templates from fixtures'

    def handle(self, *args, **options):
        self.stdout.write('Loading checklist templates...')
        
        # Read JSON file - use absolute path
        import os
        from django.conf import settings
        
        base_dir = settings.BASE_DIR
        json_file = os.path.join(base_dir, 'apps', 'checklists', 'fixtures', 'checklist_templates.json')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'✗ File not found: {json_file}')
            )
            return
        
        templates_created = 0
        templates_updated = 0
        
        for template_data in templates_data:
            code = template_data['code']
            
            # Check if template exists
            template, created = ChecklistTemplate.objects.update_or_create(
                code=code,
                defaults={
                    'name': template_data['name'],
                    'vehicle_type': template_data['vehicle_type'],
                    'description': template_data.get('description', ''),
                    'items': template_data['items'],
                    'is_system_template': template_data.get('is_system_template', True),
                    'passing_score': template_data.get('passing_score', 80),
                }
            )
            
            if created:
                templates_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created template: {code} - {template.name}')
                )
            else:
                templates_updated += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated template: {code} - {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Loaded {templates_created} new templates, '
                f'updated {templates_updated} existing templates'
            )
        )
