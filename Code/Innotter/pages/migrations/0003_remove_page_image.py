# Generated by Django 4.0.6 on 2022-08-16 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='image',
        ),
    ]
