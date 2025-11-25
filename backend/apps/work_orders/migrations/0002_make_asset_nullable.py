# Generated migration to make asset field nullable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('work_orders', '0001_initial'),
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='asset',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_orders',
                to='assets.asset'
            ),
        ),
    ]
