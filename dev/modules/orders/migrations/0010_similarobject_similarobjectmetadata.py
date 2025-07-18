# Generated by Django 5.1.3 on 2024-12-11 06:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_imageannotation'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimilarObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('link', models.URLField()),
                ('description', models.TextField(blank=True, null=True)),
                ('original_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similar_objects', to='orders.object')),
            ],
        ),
        migrations.CreateModel(
            name='SimilarObjectMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('similar_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='orders.similarobject')),
            ],
        ),
    ]
