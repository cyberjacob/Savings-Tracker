# Generated by Django 3.0.8 on 2020-07-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0005_auto_20200704_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='APR',
            field=models.DecimalField(decimal_places=4, default=0, editable=False, max_digits=6),
            preserve_default=False,
        ),
    ]
