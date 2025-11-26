# Generated migration for Firebase Authentication integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_remove_user_telegram_chat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='firebase_uid',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Unique identifier from Firebase Authentication',
                max_length=128,
                null=True,
                unique=True,
                verbose_name='Firebase UID'
            ),
        ),
    ]
