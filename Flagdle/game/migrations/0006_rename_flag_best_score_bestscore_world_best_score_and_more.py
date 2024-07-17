# Generated by Django 4.1 on 2024-07-17 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_alter_bestscore_options_alter_currentscore_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bestscore',
            old_name='flag_best_score',
            new_name='world_best_score',
        ),
        migrations.RenameField(
            model_name='currentscore',
            old_name='flag_current_score',
            new_name='world_current_score',
        ),
        migrations.AddField(
            model_name='bestscore',
            name='pride_best_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='currentscore',
            name='pride_current_score',
            field=models.IntegerField(default=0),
        ),
    ]
