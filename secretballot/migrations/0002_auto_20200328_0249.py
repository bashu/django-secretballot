# Generated by Django 3.0.4 on 2020-03-28 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretballot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='object_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='vote',
            name='vote',
            field=models.SmallIntegerField(choices=[(1, '+1'), (-1, '-1')]),
        ),
    ]