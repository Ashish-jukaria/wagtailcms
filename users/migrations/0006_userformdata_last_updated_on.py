# Generated by Django 5.1.6 on 2025-04-02 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userformdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='userformdata',
            name='last_updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
