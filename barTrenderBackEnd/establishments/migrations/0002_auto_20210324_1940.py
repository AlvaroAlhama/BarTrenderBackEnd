# Generated by Django 3.1.7 on 2021-03-24 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('establishments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='clients_id',
            field=models.ManyToManyField(blank=True, to='authentication.Client'),
        ),
    ]