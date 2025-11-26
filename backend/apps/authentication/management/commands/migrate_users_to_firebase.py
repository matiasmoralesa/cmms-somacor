"""
Django management command to migrate existing users to Firebase Authentication.

This command:
1. Finds all users without a firebase_uid
2. Creates Firebase accounts for them with temporary passwords
3. Stores the Firebase UID in the Django user model
4. Sets custom claims for each user
5. Generates a report of successful and failed migrations

Usage:
    python manage.py migrate_users_to_firebase [--dry-run] [--batch-size=50]
"""
import logging
import secrets
from typing import Dict, List, Tuple
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings

import firebase_admin
from firebase_admin import credentials

from apps.authentication.firebase_user_service import FirebaseUserService
from apps.authentication.firebase_custom_claims import CustomClaimsService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate existing Django users to Firebase Authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration in dry-run mode (no actual changes)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of users to process in each batch (default: 50)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even for users with existing firebase_uid',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        force = options['force']

        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            try:
                import os
                from pathlib import Path
                
                cred_path = settings.FIREBASE_CREDENTIALS_PATH
                if not cred_path:
                    raise CommandError('FIREBASE_CREDENTIALS_PATH not configured in settings')
                
                # Convert relative path to absolute
                if not os.path.isabs(cred_path):
                    cred_path = os.path.join(settings.BASE_DIR, cred_path)
                
                if not os.path.exists(cred_path):
                    raise CommandError(f'Firebase credentials file not found at: {cred_path}')
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL,
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
                })
                self.stdout.write(self.style.SUCCESS('✓ Firebase Admin SDK initialized'))
            except Exception as e:
                raise CommandError(f'Failed to initialize Firebase: {str(e)}')

        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('Firebase User Migration'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No changes will be made\n'))

        # Get users to migrate
        if force:
            users = User.objects.all()
            self.stdout.write(f'\nForce mode: Migrating ALL {users.count()} users')
        else:
            users = User.objects.filter(firebase_uid__isnull=True)
            self.stdout.write(f'\nFound {users.count()} users without Firebase accounts')

        if users.count() == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No users to migrate'))
            return

        # Confirm migration
        if not dry_run:
            confirm = input(f'\nProceed with migration of {users.count()} users? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('\nMigration cancelled'))
                return

        # Process users in batches
        total_users = users.count()
        successful = []
        failed = []
        skipped = []

        self.stdout.write(f'\nProcessing {total_users} users in batches of {batch_size}...\n')

        for i in range(0, total_users, batch_size):
            batch = users[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_users + batch_size - 1) // batch_size

            self.stdout.write(f'\nBatch {batch_num}/{total_batches}:')

            for user in batch:
                result = self._migrate_user(user, dry_run, force)
                
                if result['status'] == 'success':
                    successful.append(result)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {user.email} -> {result["firebase_uid"]}')
                    )
                elif result['status'] == 'skipped':
                    skipped.append(result)
                    self.stdout.write(
                        self.style.WARNING(f'  ⊘ {user.email} - {result["reason"]}')
                    )
                else:
                    failed.append(result)
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {user.email} - {result["error"]}')
                    )

        # Print summary
        self._print_summary(successful, failed, skipped, dry_run)

        # Generate report file
        if not dry_run:
            self._generate_report(successful, failed, skipped)

    def _migrate_user(self, user: User, dry_run: bool, force: bool) -> Dict:
        """
        Migrate a single user to Firebase.
        
        Returns:
            Dict with status, user info, and result details
        """
        try:
            # Skip if user already has firebase_uid (unless force mode)
            if user.firebase_uid and not force:
                return {
                    'status': 'skipped',
                    'user_id': str(user.id),
                    'email': user.email,
                    'reason': 'Already has firebase_uid',
                }

            if dry_run:
                return {
                    'status': 'success',
                    'user_id': str(user.id),
                    'email': user.email,
                    'firebase_uid': 'DRY_RUN_UID',
                    'temp_password': 'DRY_RUN_PASSWORD',
                }

            # Generate temporary password
            temp_password = self._generate_temp_password()

            # Create Firebase user
            display_name = user.get_full_name() or user.email
            firebase_uid = FirebaseUserService.create_firebase_user(
                email=user.email,
                password=temp_password,
                display_name=display_name,
                disabled=not user.is_active
            )

            # Update Django user with Firebase UID
            with transaction.atomic():
                User.objects.filter(pk=user.pk).update(firebase_uid=firebase_uid)
                user.refresh_from_db()

            # Set custom claims
            CustomClaimsService.update_user_claims(user)

            return {
                'status': 'success',
                'user_id': str(user.id),
                'email': user.email,
                'firebase_uid': firebase_uid,
                'temp_password': temp_password,
            }

        except Exception as e:
            logger.error(f'Failed to migrate user {user.email}: {str(e)}')
            return {
                'status': 'failed',
                'user_id': str(user.id),
                'email': user.email,
                'error': str(e),
            }

    def _generate_temp_password(self) -> str:
        """Generate a secure temporary password."""
        # Generate a 20-character password with letters, digits, and special chars
        return secrets.token_urlsafe(20)

    def _print_summary(
        self,
        successful: List[Dict],
        failed: List[Dict],
        skipped: List[Dict],
        dry_run: bool
    ):
        """Print migration summary."""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('Migration Summary'))
        self.stdout.write('='*80 + '\n')

        total = len(successful) + len(failed) + len(skipped)
        
        self.stdout.write(f'Total users processed: {total}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Successful: {len(successful)}'))
        self.stdout.write(self.style.ERROR(f'  ✗ Failed: {len(failed)}'))
        self.stdout.write(self.style.WARNING(f'  ⊘ Skipped: {len(skipped)}'))

        if failed:
            self.stdout.write('\n' + self.style.ERROR('Failed Migrations:'))
            for result in failed:
                self.stdout.write(f'  - {result["email"]}: {result["error"]}')

        if not dry_run and successful:
            self.stdout.write('\n' + self.style.WARNING('⚠️  IMPORTANT:'))
            self.stdout.write('Users have been created with temporary passwords.')
            self.stdout.write('Run the following command to send password reset emails:')
            self.stdout.write(self.style.SUCCESS('  python manage.py send_migration_emails'))

    def _generate_report(
        self,
        successful: List[Dict],
        failed: List[Dict],
        skipped: List[Dict]
    ):
        """Generate a detailed migration report file."""
        import json
        from datetime import datetime
        from pathlib import Path

        report_dir = Path('migration_reports')
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'firebase_migration_{timestamp}.json'

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(successful) + len(failed) + len(skipped),
                'successful': len(successful),
                'failed': len(failed),
                'skipped': len(skipped),
            },
            'successful_migrations': successful,
            'failed_migrations': failed,
            'skipped_users': skipped,
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.stdout.write(f'\n✓ Report saved to: {report_file}')

        # Also save temporary passwords to a secure file
        if successful:
            passwords_file = report_dir / f'temp_passwords_{timestamp}.txt'
            with open(passwords_file, 'w') as f:
                f.write('TEMPORARY PASSWORDS - DELETE AFTER SENDING RESET EMAILS\n')
                f.write('='*80 + '\n\n')
                for result in successful:
                    f.write(f'{result["email"]}: {result["temp_password"]}\n')

            self.stdout.write(f'✓ Temporary passwords saved to: {passwords_file}')
            self.stdout.write(self.style.WARNING('\n⚠️  DELETE THIS FILE AFTER SENDING PASSWORD RESET EMAILS'))
