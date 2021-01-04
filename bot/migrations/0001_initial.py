# Generated by Django 3.1.5 on 2021-01-04 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArkFund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=4)),
                ('file_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='ArkStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=1024)),
                ('ticker', models.CharField(blank=True, max_length=30)),
                ('shares', models.IntegerField(blank=True, default=0)),
                ('shares_delta', models.IntegerField(blank=True, null=True)),
                ('shares_delta_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('weight_delta', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('had_changes', models.BooleanField(default=False)),
                ('fund', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='bot.arkfund')),
            ],
        ),
    ]