"""
Migration to add telegram_chat_id to User model
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='telegram_chat_id',
            field=models.CharField(max_length=100, null=True, blank=True, help_text='Telegram chat ID for notifications'),
        ),
    ]
