"""
Django management command to send password reset emails to migrated users.

This command:
1. Finds all users with firebase_uid
2. Sends password reset emails via Firebase
3. Logs the results

Usage:
    python manage.py send_migration_emails [--dry-run] [--batch-size=50] [--email=user@example.com]
"""
import logging
import time
from typing import Dict, List
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings

import firebase_admin
from firebase_admin import credentials

from apps.authentication.firebase_user_service import FirebaseUserService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send password reset emails to users migrated to Firebase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode (no emails sent)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of emails to send in each batch (default: 50)',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Send email to a specific user (by email address)',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay in seconds between emails (default: 1.0)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        specific_email = options['email']
        delay = options['delay']

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
        self.stdout.write(self.style.SUCCESS('Firebase Password Reset Email Sender'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No emails will be sent\n'))

        # Get users to send emails to
        if specific_email:
            users = User.objects.filter(email=specific_email, firebase_uid__isnull=False)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'\n✗ User not found: {specific_email}'))
                return
            self.stdout.write(f'\nSending email to: {specific_email}')
        else:
            users = User.objects.filter(firebase_uid__isnull=False, is_active=True)
            self.stdout.write(f'\nFound {users.count()} users with Firebase accounts')

        if users.count() == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No users to send emails to'))
            return

        # Confirm sending
        if not dry_run and not specific_email:
            confirm = input(f'\nSend password reset emails to {users.count()} users? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('\nOperation cancelled'))
                return

        # Process users in batches
        total_users = users.count()
        successful = []
        failed = []

        self.stdout.write(f'\nProcessing {total_users} users...\n')

        for i, user in enumerate(users, 1):
            result = self._send_password_reset_email(user, dry_run)
            
            if result['status'] == 'success':
                successful.append(result)
                self.stdout.write(
                    self.style.SUCCESS(f'  [{i}/{total_users}] ✓ {user.email}')
                )
            else:
                failed.append(result)
                self.stdout.write(
                    self.style.ERROR(f'  [{i}/{total_users}] ✗ {user.email} - {result["error"]}')
                )

            # Add delay between emails to avoid rate limiting
            if not dry_run and i < total_users:
                time.sleep(delay)

            # Print progress every batch_size users
            if i % batch_size == 0:
                self.stdout.write(f'\n  Progress: {i}/{total_users} ({i*100//total_users}%)\n')

        # Print summary
        self._print_summary(successful, failed, dry_run)

    def _send_password_reset_email(self, user: User, dry_run: bool) -> Dict:
        """
        Send password reset email to a user.
        
        Returns:
            Dict with status and result details
        """
        try:
            if dry_run:
                return {
                    'status': 'success',
                    'user_id': str(user.id),
                    'email': user.email,
                }

            # Send password reset email via Firebase
            FirebaseUserService.send_password_reset_email(user.email)

            return {
                'status': 'success',
                'user_id': str(user.id),
                'email': user.email,
            }

        except Exception as e:
            logger.error(f'Failed to send password reset email to {user.email}: {str(e)}')
            return {
                'status': 'failed',
                'user_id': str(user.id),
                'email': user.email,
                'error': str(e),
            }

    def _print_summary(self, successful: List[Dict], failed: List[Dict], dry_run: bool):
        """Print email sending summary."""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('Email Sending Summary'))
        self.stdout.write('='*80 + '\n')

        total = len(successful) + len(failed)
        
        self.stdout.write(f'Total emails processed: {total}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Sent successfully: {len(successful)}'))
        self.stdout.write(self.style.ERROR(f'  ✗ Failed: {len(failed)}'))

        if failed:
            self.stdout.write('\n' + self.style.ERROR('Failed Emails:'))
            for result in failed:
                self.stdout.write(f'  - {result["email"]}: {result["error"]}')

        if not dry_run and successful:
            self.stdout.write('\n' + self.style.SUCCESS('✓ Password reset emails sent successfully'))
            self.stdout.write('\nUsers should receive emails with instructions to reset their passwords.')
            self.stdout.write('The emails will be sent from Firebase Authentication.')
