# Generated by Django 5.1.3 on 2025-03-25 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=10),
        ),
    ]
