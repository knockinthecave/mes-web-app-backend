# Generated by Django 3.2.2 on 2023-08-30 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalWarhousing',
            fields=[
                ('uid', models.IntegerField(primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=30)),
                ('partNumber', models.CharField(max_length=30)),
                ('quantity', models.IntegerField()),
                ('lotNo', models.CharField(max_length=30)),
                ('warehousingDate', models.DateField()),
                ('warehousingWorker', models.CharField(max_length=30)),
                ('note', models.CharField(max_length=100)),
                ('warehouse_location', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'external_warehousing',
                'managed': False,
            },
        ),
    ]
