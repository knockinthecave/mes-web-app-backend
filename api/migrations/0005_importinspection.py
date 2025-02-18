# Generated by Django 3.2.2 on 2023-09-06 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_bom'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportInspection',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=30)),
                ('partNumber', models.CharField(max_length=30)),
                ('quantity', models.IntegerField()),
                ('quantity2', models.CharField(max_length=10)),
                ('lotNo', models.CharField(max_length=30)),
                ('importInspectionDate', models.DateTimeField()),
                ('importInspectionWorker', models.CharField(max_length=100)),
                ('Location', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'importInspection',
                'managed': False,
            },
        ),
    ]
