# Generated by Django 3.1.5 on 2021-01-05 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='arkfund',
            name='update_now',
            field=models.BooleanField(default=True),
        ),
    ]
