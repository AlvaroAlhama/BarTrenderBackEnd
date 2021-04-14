# Generated by Django 3.1.4 on 2021-04-13 21:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_date', models.DateField()),
                ('filter_enum', models.CharField(choices=[('Ambiente', 'A'), ('Bebida', 'B'), ('Estilo', 'E'), ('Instalacion', 'I'), ('Ocio', 'O'), ('Tapa', 'T')], max_length=25)),
                ('type_text', models.CharField(max_length=100)),
                ('value_number', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('zone_enum', models.CharField(blank=True, choices=[('Alameda', 'Al'), ('Triana', 'Tr'), ('Macarena', 'Mc'), ('Remedios', 'Rm'), ('Bermejales', 'B'), ('Cartuja', 'C'), ('Nervion', 'N'), ('San Bernardo', 'Sb'), ('Sevilla Este', 'Se'), ('Bellavista', 'Be'), ('Exterior', 'Ex')], max_length=25, null=True)),
            ],
        ),
    ]
