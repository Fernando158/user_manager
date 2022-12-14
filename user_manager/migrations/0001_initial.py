# Generated by Django 4.1 on 2022-08-10 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='operation_logs',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('method', models.CharField(db_index=True, max_length=10)),
                ('status_code', models.PositiveSmallIntegerField(db_index=True, help_text='Response status code')),
                ('operation', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Operation Log',
                'verbose_name_plural': 'Operation Logs',
                'db_table': 'operation_logs',
            },
        ),
    ]
