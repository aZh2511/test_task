# Generated by Django 3.1.6 on 2021-02-05 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alias', '0003_auto_20210205_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alias',
            name='end',
            field=models.DateTimeField(blank=True),
        ),
    ]
