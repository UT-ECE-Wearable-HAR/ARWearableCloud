# Generated by Django 3.1.2 on 2021-02-12 03:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0004_merge_20210211_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imgcapture',
            name='date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]