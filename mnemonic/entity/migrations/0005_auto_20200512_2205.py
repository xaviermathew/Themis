# Generated by Django 3.0.5 on 2020-05-12 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_auto_20200425_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='twitter_handle',
            field=models.CharField(default='DUMMY', max_length=256, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='person',
            name='twitter_handle',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
