# Generated by Django 4.2.1 on 2023-05-19 17:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="daily_fee",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=6,
                validators=[django.core.validators.MinValueValidator(0.0)],
            ),
        ),
    ]